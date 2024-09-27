from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Your bot API details
API_ID = "24583730"
API_HASH = "cc02358562bc1ebf7999106298defb21"
BOT_TOKEN = "7234753304:AAFY9BKOqjPETb6rpngE1GY6IqHqWfglyEk"
SERVICE_CITY = "Shanghai"  # Example service city, update as necessary
CHANNEL_USERNAME = "@PinDaoA1"  # Channel where the order will be sent
CUSTOMER_SERVICE = "@Ethan666888"  # Customer service contact

app = Client("bot_b", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# This dictionary stores the order information per user
orders = {}

# Step 1: Ask for the address
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Welcome! Please provide your address to check if we can serve you:")

# Step 2: Verify the address
@app.on_message(filters.text & filters.private)
async def check_address(client, message):
    user_id = message.from_user.id
    address = message.text.lower()

    if SERVICE_CITY.lower() in address:
        orders[user_id] = {"address": address}  # Store the address
        # Show product menu if within service area
        await show_product_menu(client, message)
    else:
        await message.reply("Sorry, we cannot provide service to your area.")

# Step 3: Show the product selection menu
async def show_product_menu(client, message):
    buttons = [
        [InlineKeyboardButton("Product 1", callback_data="product1"), InlineKeyboardButton("Product 2", callback_data="product2")],
        [InlineKeyboardButton("Product 3", callback_data="product3")]
    ]
    # Use message.reply to ensure the bot is the one sending the message
    await message.reply("Please select a product:", reply_markup=InlineKeyboardMarkup(buttons))

# Step 4: Handle product selection and initialize the order
@app.on_callback_query(filters.regex("product"))
async def select_product(client, callback_query):
    product = callback_query.data
    user_id = callback_query.from_user.id

    # Ensure that the user has an entry in the orders dictionary
    if user_id not in orders:
        orders[user_id] = {}  # Initialize if not already present

    orders[user_id]["product"] = product  # Store selected product

    # Show quantity options
    buttons = [
        [InlineKeyboardButton("Quantity 1", callback_data="quantity1"), InlineKeyboardButton("Quantity 2", callback_data="quantity2")],
        [InlineKeyboardButton("Quantity 3", callback_data="quantity3")]
    ]
    await callback_query.message.edit_text("Please select the quantity:", reply_markup=InlineKeyboardMarkup(buttons))

# Step 5: Handle quantity selection and complete the order
@app.on_callback_query(filters.regex("quantity"))
async def select_quantity(client, callback_query):
    quantity = callback_query.data
    user_id = callback_query.from_user.id

    # Ensure the user has already selected a product and initialized an order
    if user_id not in orders:
        await callback_query.message.reply("Error: You need to select a product first.")
        return

    orders[user_id]["quantity"] = quantity  # Store selected quantity

    # Retrieve user information
    user = callback_query.from_user
    user_info = f"User ID: {user_id}"
    
    if user.username:
        user_info += f"\nUsername: @{user.username}"  # Include username if available
    else:
        user_info += f"\nName: {user.first_name} {user.last_name or ''}"  # Use full name if no username

    # Send order details to the channel
    order_info = orders[user_id]
    await client.send_message(
        CHANNEL_USERNAME,
        f"New order:\n{user_info}\nAddress: {order_info['address']}\nProduct: {order_info['product']}\nQuantity: {order_info['quantity']}"
    )

    # Ask if they need anything else
    buttons = [
        [InlineKeyboardButton("Need More", callback_data="need_more"), InlineKeyboardButton("Do Not Need", callback_data="do_not_need")]
    ]
    await callback_query.message.edit_text("Your product has been packaged. Do you need anything else?", reply_markup=InlineKeyboardMarkup(buttons))

# Step 6: Handle the "Need More" and "Do Not Need" options
@app.on_callback_query(filters.regex("need_more"))
async def need_more(client, callback_query):
    user_id = callback_query.from_user.id

    # Repeat product selection without sending new messages
    await show_product_menu(client, callback_query.message)

@app.on_callback_query(filters.regex("do_not_need"))
async def do_not_need(client, callback_query):
    user_id = callback_query.from_user.id

    # Final message to user
    await callback_query.message.edit_text(f"Your product has been packaged. Please contact customer service {CUSTOMER_SERVICE} in the channel to obtain the payment link.")
    # Optionally, you can also clear the user's order data if needed
    orders.pop(user_id, None)  # Clear the order data

app.run()
