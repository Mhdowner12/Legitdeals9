# Additional option to send a test message and leave groups where sending fails
async def send_test_message_and_leave(api_id, api_hash, phone_number, session_name):
    client = TelegramClient(session_name, api_id, api_hash)
    
    await client.start(phone=phone_number)
    
    test_message = "Dm for Buy @Megix_Ott\nChannel @legitdeals99\nProofs @legitproofs99"
    
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            group = dialog.entity
            try:
                await client.send_message(group, test_message)
                print(Fore.GREEN + f"Test message sent to {group.title}")
            except (ChannelPrivateError, PeerIdInvalidError) as e:
                print(Fore.RED + f"Cannot send message to {group.title} (banned or access restricted). Leaving group.")
                await client(LeaveChannelRequest(group))
            except Exception as e:
                print(Fore.RED + f"Failed to send message to {group.title}: {str(e)}. Leaving group.")
                await client(LeaveChannelRequest(group))
    
    await client.disconnect()

async def main():
    display_banner()

    num_sessions = int(input("How many sessions would you like to log in? "))  # Ask for the number of sessions
    tasks = []

    for i in range(1, num_sessions + 1):
        session_name = f'session{i}'
        credentials = load_credentials(session_name)

        if credentials:
            print(f"\nUsing saved credentials for session {i}.")
            api_id = credentials['api_id']
            api_hash = credentials['api_hash']
            phone_number = credentials['phone_number']
        else:
            print(f"\nEnter details for account {i}:")
            api_id = int(input(f"Enter API ID for session {i}: "))
            api_hash = input(f"Enter API hash for session {i}: ")
            phone_number = input(f"Enter phone number for session {i} (with country code): ")

            credentials = {
                'api_id': api_id,
                'api_hash': api_hash,
                'phone_number': phone_number
            }
            save_credentials(session_name, credentials)

        choice = int(input(f"\nSelect action for session {i}:\n1. AutoSender\n2. Leave Groups\n3. Test Message and Leave\nEnter choice: "))
        if choice == 1:
            repeat_count = int(input(f"How many rounds to forward messages for session {i}? "))
            delay_after_all_groups = int(input(f"Enter delay (in seconds) after forwarding to all groups for session {i}: "))
            tasks.append(login_and_forward(api_id, api_hash, phone_number, session_name, repeat_count, delay_after_all_groups))
        elif choice == 2:
            client = TelegramClient(session_name, api_id, api_hash)
            await client.start(phone=phone_number)
            tasks.append(leave_unwanted_groups(client))
        elif choice == 3:
            tasks.append(send_test_message_and_leave(api_id, api_hash, phone_number, session_name))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
