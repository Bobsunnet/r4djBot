import config

failed_to_send_order_message = (
    f"Не вдалося обробити ваше замовлення. {config.reload_help_message}"
)

date_format_message = "\ndd.mm.yy - dd.mm.yy\n(день.місяць.рік)"

not_authorized_message = "На жаль, ви ще не зареєстровані в системі. Спочатку пройдіть реєстрацію, щоб мати можливість оформити замовлення"

order_processing_message = "✅Ваше замовлення прийнято"

enter_name_message = "Введіть ваше Ім’я."
enter_surname_message = "Введіть ваше Прізвище."
reload_help_message = "Спробуйте ще раз, перезавнтаживши бота командою /start"
