import util


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                util.send_message_to_telebot(f'Error occurred: {str(e)}')
            except Exception as ex:
                print(ex)
            raise e

    return wrapper


def exception_handler_async(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if args and hasattr(args[0], "send"):
                try:
                    await args[0].send(str(e))
                except Exception as ex:
                    print(ex)
            else:
                try:
                    util.send_message_to_telebot(f'Error occurred: {str(e)}')
                except Exception as ex:
                    print(ex)
            print(f"Exception in {func.__name__}: {e}")

    return wrapper
