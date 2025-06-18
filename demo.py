import os
from web3 import Web3
import json
from dotenv import load_dotenv, find_dotenv
from alith import Agent, WindowBufferMemory, MilvusStore, chunk_text
from pathlib import Path

# Load environment variables
loaded = load_dotenv(find_dotenv(), override=True)
print("DEBUG: .env loaded =", loaded)

# Metis Hyperion Configuration
METIS_HYPERION_CONFIG = {
    'chain_id': 133717,
    'rpc_url': 'https://hyperion-testnet.metisdevops.link',
    'explorer_url': 'https://hyperion-testnet-explorer.metisdevops.link/',
    'name': 'Metis Hyerion Testnet',
}

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(METIS_HYPERION_CONFIG['rpc_url']))

# ERC20 ABI (minimal for balance checks)
ERC20_ABI = '''[
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "internalType": "uint8",
                "name": "",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]'''

# Create knowledge base content for RAG
def create_knowledge_base():
    """Create a knowledge base with Metis L2 and ERC20 information"""
    
    knowledge_content = """
    # Metis L2 Blockchain Information
    
    ## What is Metis?
    Metis is a Layer 2 scaling solution for Ethereum that provides fast and low-cost transactions.
    It uses Optimistic Rollup technology to achieve scalability while maintaining security.
    
    ## Metis Hyperion Testnet
    - Chain ID: 133717
    - RPC URL: https://hyperion-testnet.metisdevops.link
    - Explorer: https://hyperion-testnet-explorer.metisdevops.link
    - Purpose: Testing environment for developers
    
    ## ERC20 Tokens
    ERC20 is a technical standard for fungible tokens on Ethereum and compatible blockchains like Metis.
    
    ### Key ERC20 Functions:
    - balanceOf(address): Returns token balance of an address
    - decimals(): Returns number of decimal places for the token
    - name(): Returns the full name of the token
    - symbol(): Returns the trading symbol
    - totalSupply(): Returns total token supply
    
    ### Token Decimals Explained:
    Most tokens use 18 decimals (like Ethereum's Wei system).
    To convert raw balance to human-readable format:
    Human Balance = Raw Balance / (10 ^ decimals)
    
    Example: If raw balance is 500000000 and decimals is 18,
    then human balance is 1.0 tokens.
    
    ## Common Token Decimal Values:
    - 18 decimals: Most standard tokens (USDC, DAI, etc.)
    - 6 decimals: USDT, some stablecoins
    - 8 decimals: Some Bitcoin-pegged tokens
    
    ## Wallet Address Validation:
    Valid Ethereum/Metis addresses:
    - Must be 42 characters long
    - Must start with '0x'
    - Must contain only hexadecimal characters (0-9, a-f, A-F)
    
    ## Transaction Troubleshooting:
    - Invalid address format: Check length and hex characters
    - Contract not found: Verify contract address on explorer
    - RPC errors: Network connectivity or node issues
    
    ## Best Practices:
    - Always validate addresses before making calls
    - Handle contract call exceptions gracefully
    - Display both raw and formatted balances for transparency
    - Use proper decimal formatting based on token decimals
    """
    
    # Save knowledge to a file
    knowledge_file = Path("metis_knowledge.md")
    knowledge_file.write_text(knowledge_content)
    return knowledge_file

# Initialize RAG with Vector Database
def setup_rag():
    """Setup RAG with knowledge base"""
    try:
        # Create knowledge base file
        knowledge_file = create_knowledge_base()
        
        # Create MilvusStore for vector database
        store = MilvusStore().save_docs(
            chunk_text(knowledge_file.read_text())
        )
        
        print("✅ RAG knowledge base initialized successfully!")
        return store
    except Exception as e:
        print(f"⚠️ RAG setup failed: {e}")
        print("Continuing without RAG...")
        return None

# Setup RAG
rag_store = setup_rag()

# Initialize Alith Agent with WindowBufferMemory and RAG
agent = Agent(
    name="Metis Token Balance Agent with RAG",
    model="gpt-4",
    preamble="""You are an AI assistant for Metis L2 that can check ERC20 token balances and answer technical questions using a knowledge base.
        You are connected to a vector search system (RAG) that contains important documentation about:
        - Metis L2 blockchain and its features
        - ERC20 token standards and functions
        - Token decimals and formatting rules
        - Blockchain address validation and troubleshooting

        When answering technical or factual questions, **you must rely only on the knowledge base content** unless otherwise specified. Do not make assumptions or use outside knowledge if the RAG context is available.

        Behavior:
        - When asked informational questions (e.g., about Metis, ERC20, decimals), retrieve and quote or summarize relevant chunks from the knowledge base.
        - If the user’s request cannot be answered from the knowledge base, say so clearly.
        - You have access to memory and conversation history to assist with follow-ups and context-aware responses.""",
    memory=WindowBufferMemory(),
    store=rag_store if rag_store else None
)

def is_valid_address(address: str) -> bool:
    """Validate Ethereum address format"""
    return address and len(address) == 42 and address.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in address[2:])

def check_balance(contract_address: str, wallet_address: str) -> str:
    try:
        # Validate addresses
        if not is_valid_address(contract_address) or not is_valid_address(wallet_address):
            return "❌ Invalid address format. Addresses should be 42 characters long and start with '0x'"

        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=json.loads(ERC20_ABI)
        )
        
        # Get token info
        try:
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            name = contract.functions.name().call()
            total_supply = contract.functions.totalSupply().call()
        except Exception as e:
            return f"❌ Error reading token information: {str(e)}"
        
        # Get balance
        balance = contract.functions.balanceOf(
            Web3.to_checksum_address(wallet_address)
        ).call()
        
        # Format balance using the decimals retrieved from the contract
        formatted_balance = balance / (10 ** decimals)
        formatted_total_supply = total_supply / (10 ** decimals)
        
        return (
            f"💰 Token Balance Report\n\n"
            f"Token Name: {name}\n"
            f"Symbol: {symbol}\n"
            f"Total Supply: {formatted_total_supply:,.2f} {symbol}\n"
            f"Decimals: {decimals}\n\n"
            f"Wallet: {wallet_address}\n"
            f"Balance: {formatted_balance:,.{decimals}f} {symbol}\n"
            f"Raw Balance: {balance}\n\n"
            f"🔍 View on Explorer:\n"
            f"Token: {METIS_HYPERION_CONFIG['explorer_url']}/token/{contract_address}\n"
            f"Wallet: {METIS_HYPERION_CONFIG['explorer_url']}/address/{wallet_address}"
        )
    
    except Exception as e:
        return f"❌ Error checking balance: {str(e)}"

def main():
    print(f"🤖 Metis Token Balance Agent with RAG running on {METIS_HYPERION_CONFIG['name']}...")
    print("This agent can check ERC20 token balances, remembers our conversation,")
    print("and has access to knowledge about Metis L2 and ERC20 tokens!")
    print("Type 'exit' to quit.")
    print("\nCommands:")
    print("- check <contract_address> <wallet_address>  (Check token balance)")
    print("- Ask questions about Metis L2, ERC20 tokens, or blockchain concepts")
    print("- Or just chat naturally - I'll remember our conversation!")
    
    # Show RAG status
    if rag_store:
        print("✅ RAG Knowledge Base: Active")
    else:
        print("⚠️ RAG Knowledge Base: Disabled")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            response = agent.prompt("The user is saying goodbye. Give a friendly farewell message.")
            print(f"Agent: {response}")
            break
        
        # Check if this is a balance check request
        if user_input.lower().startswith("check "):
            parts = user_input.split()
            if len(parts) >= 3:
                contract_address = parts[1]
                wallet_address = parts[2]
                
                print("🔍 Checking token balance...")
                balance_result = check_balance(contract_address, wallet_address)
                
                # Pass the balance result to the agent so it can remember it
                agent_prompt = f"I just checked a token balance for the user. Here are the results:\n\n{balance_result}\n\nPlease acknowledge this information, provide any relevant insights from your knowledge base about the token or Metis L2, and ask if they need anything else."
                response = agent.prompt(agent_prompt)
                print(f"Agent: {response}")
            else:
                error_msg = "Please provide both contract and wallet addresses. Example: check 0x123... 0x456..."
                response = agent.prompt(f"The user tried to use the check command but didn't provide enough parameters. The error message is: {error_msg}. Please explain the correct format and provide helpful information from your knowledge base.")
                print(f"Agent: {response}")
        else:
            # Handle with the AI agent for other queries - it will use RAG and remember context
            response = agent.prompt(user_input)
            print(f"Agent: {response}")

if __name__ == "__main__":
    main()
