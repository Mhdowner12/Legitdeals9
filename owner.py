import asyncio
from pyrogram import Client
from colorama import Fore, Style, init
from pyfiglet import Figlet

init(autoreset=True)

# Function to print the name in big letters
def print_big_name():
    figlet = Figlet(font='big')
    big_name = figlet.renderText('LEGITDEALS9')
    print(Fore.RED + big_name)

def generate_auth_key():
    raise Exception('No authorization key provided. Please enter a valid key.')

async def get_chat_ids(app: Client):
    chat_ids = []
    chat_with_topic = {}
    async for dialog in app.get_dialogs():
        if hasattr(dialog.chat, 'is_forum') and dialog.chat.is_forum:
            try:
                chat_with_topic[dialog.chat.id] = dialog.top_message.topics.id
            except AttributeError:
                pass
        chat_ids.append(dialog.chat.id)

    chat_ids = [str(chat_id) for chat_id in chat_ids if str(chat_id).startswith('-')]
    chat_ids = [int(chat_id) for chat_id in chat_ids]
    return chat_ids, chat_with_topic

async def send_last_message_to_groups(apps, timee, numtime):
    async def send_last_message(app: Client):
        try:
            chat_ids, chat_with_topic = await get_chat_ids(app)
            if not chat_ids:
                print(f"{Fore.RED}No chats found.")
                return

            # Get the last message from a valid chat
            last_message = None
            async for message in app.get_chat_history(chat_ids[0], limit=1):
                last_message = message.id
                break

            if last_message:
                for chat_id in chat_with_topic:
                    try:
                        await app.forward_messages(chat_id=chat_id, from_chat_id=chat_ids[0], message_ids=last_message, message_thread_id=chat_with_topic[chat_id])
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                    except Exception as e:
                        print(f"{Fore.RED}Failed to send message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(2)

                for chat_id in chat_ids:
                    try:
                        await app.forward_messages(chat_id, chat_ids[0], last_message)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"{Fore.RED}Failed to send message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(5)
            else:
                print(f"{Fore.RED}No last message found.")

            await asyncio.sleep(timee)

        except Exception as e:
            print(f"{Fore.RED}Error in sending last message: {e}")

    await asyncio.gather(*(send_last_message(app) for app in apps))

async def main():
    print_big_name()  # Print the name in big letters

    try:
        num_sessions = int(input("Enter the number of sessions: "))
    except ValueError:
        print(f"{Fore.RED}Invalid number of sessions.")
        return

    apps = []
    for i in range(num_sessions):
        session_name = f"my_account{i+1}"
        try:
            app = Client(session_name)
            await app.start()
        except Exception as e:
            print(f"{Fore.RED}Failed to start session {session_name}: {e}")
            try:
                api_id = int(input(f"Enter API ID for {session_name} (LEGITDEALS9): "))
                api_hash = input(f"Enter API hash for {session_name} (LEGITDEALS9): ")
                app = Client(session_name, api_id=api_id, api_hash=api_hash)
                await app.start()
            except ValueError:
                print(f"{Fore.RED}Invalid API ID or API hash.")
                return
            except Exception as e:
                print(f"{Fore.RED}Failed to start session {session_name} with provided credentials: {e}")
                return
        apps.append(app)

    while True:
        try:
            choice = int(input(f"{Style.BRIGHT}{Fore.YELLOW}2. AutoSender\n6. Exit\nEnter your choice: {Style.RESET_ALL}"))
        except ValueError:
            print(f"{Fore.RED}Invalid choice.")
            continue

        if choice == 2:
            try:
                numtime = int(input("How many times you want to send the message: "))
                timee = int(input("Enter the time delay: "))
                await send_last_message_to_groups(apps, timee, numtime)
            except ValueError:
                print(f"{Fore.RED}Invalid number.")
            except Exception as e:
                print(f"{Fore.RED}Error occurred: {e}")

        elif choice == 6:
            for app in apps:
                await app.stop()
            break

        else:
            print(f"{Fore.RED}Invalid choice.")

if __name__ == "__main__":
    asyncio.run(main())
