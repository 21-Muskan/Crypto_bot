A Simple Binance Futures Trading Bot

Hey there! This is a little Python bot that chats with the Binance Futures Testnet (USDT-M). It's a command-line tool, which just means you'll type commands to it, and it'll let you place market, limit, and even stop-limit orders.

I built this to check off all the boxes for that application task, including the bonus stuff!

:sparkles: What It Can Do (Features)

Testnet Only: No real money here! It's all set up to use the https://testnet.binancefuture.com site.

Built to be Reused: All the main logic is packed into a BasicBot class, so you can tinker with it or build on top of it.

Order Types Supported:

MARKET (the "get it now" order)

LIMIT (the "buy/sell at this price" order)

STOP_LIMIT (the "get ready to place a limit order" one)

Buy or Sell: Does both BUY and SELL orders, no problem.

Friendly CLI: You get a nice little menu to:

Place a new order.

Check on an order you already placed.

See how much (test) USDT you have.

Checks Your Input: It tries to catch typos or mistakes before sending anything to Binance.

Keeps a Log: It jots down everything it does (actions, API chatter, errors) into a file at logs/trading_bot.log. It also prints to your screen, of course!

Keeps Keys Safe: It'll look for a .env file to keep your API keys secret, or it'll ask you for them in a way that doesn't show them on screen.

1. :key: First Things First: Get Your Testnet Keys

Super Important! You have to get your keys from the Binance Testnet. Your regular Binance.com keys won't work here.

Sign Up / Log In: Head over to the Binance Futures Testnet and get yourself logged in.

Get Your Keys:

Look for the "API Key" section. It's usually on your dashboard somewhere.

Make a new key.

Make sure you check the "Enable Futures" and "Enable Trading" boxes!

Copy your API Key and Secret Key right away. You'll only see the Secret Key once, so stash it somewhere safe!

2. :rocket: Let's Get This Set Up!

Just follow these steps, and you'll be ready to go.

Step 1: Get the Files

Just grab all the files (trading_bot.py, requirements.txt, etc.) and put them in a new folder (like your d:\internship one).

Step 2: Install the Goodies

It's always a good idea to use a virtual environment (venv) for Python stuff. It keeps things tidy!

First, make a venv (this is optional, but a really good habit!)
python -m venv venv

Now, turn it on
On Windows (that's you!):
.\venv\Scripts\activate

If you were on macOS/Linux, you'd type:
source vVenv/bin/activate

Last, install the packages this bot needs
pip install -r requirements.txt


Step 3: Set Up Your Keys

The easiest way to do this is with a .env file.

In your PS D:\internship> prompt, just rename that .env.example file to .env.

This works in PowerShell (PS) or the old Command Prompt (cmd)
rename .env.example .env

You could also just copy it
cp .env.example .env


Open up that new .env file with any text editor (like VS Code or Notepad) and paste your keys in, just like this:

.env file
Your API keys from [https://testnet.binancefuture.com/](https://testnet.binancefuture.com/)
BINANCE_TEST_KEY="your_api_key_goes_here"
BINANCE_TEST_SECRET="your_secret_key_goes_here"


Heads-up: If you skip this step, don't worry! The script will just ask you for your keys when it starts. (That's what you saw happen before!)

3. :computer: How to Run the Bot

With your virtual environment activated ((venv) PS D:\internship>) and dependencies installed, run the main Python script:

python trading_bot.py


If you created the .env file correctly, the bot will start immediately.

You will be greeted by the main menu:

=========================================
=   Binance Futures Testnet Trading Bot =
=========================================
...
--- Main Menu ---
1: Place New Order
2: Check Order Status
3: Check USDT Balance
4. Exit
Enter your choice (1-4):


Simply follow the on-screen prompts to place orders, check your balance, or look up order details. All activity will be printed to the console and saved in the logs/trading_bot.log file.
