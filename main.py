import json, re
import web3, web3.tools, web3.contract, web3.exceptions, web3.middleware
from web3 import Web3
from getpass import getpass
from web3.exceptions import ContractLogicError

with open('abi.json', 'r') as f:
    abi = json.load(f)
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
w3.middleware_onion.inject(web3.middleware.geth_poa.geth_poa_middleware, layer=0	)

main_address = Web3.to_checksum_address("0x3df0d3d1c811fe61f560cdf034a65d26e80a1a20")
user_address = ""

for item in w3.eth.accounts:
	if item != main_address:
		w3.geth.personal.lock_account(item)

contractAddress = Web3.to_checksum_address("0x4c919EBb8d0224DcfB0243DEA12e0b2Db711CB7C")
contract = w3.eth.contract(contractAddress, abi=abi)


def is_strong_password(password):
    if len(password) < 12:
        print("Пароль должен быть не менее 12 символов")
        return False
    if not re.search(r'[A-Z]', password):
        print("Пароль должен содержать хотя бы одну заглавную букву")
        return False
    if not re.search(r'[a-z]', password):
        print("Пароль должен содержать хотя бы одну строчную букву")
        return False
    if not re.search(r'\d', password):
        print("Пароль должен содержать хотя бы одну цифру")
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        print("Пароль должен содержать хотя бы один специальный символ")
        return False
    common_patterns = ["password", "123456", "123456789", "qwerty", "abc123", "password1", "qwerty123"]
    for pattern in common_patterns:
        if pattern in password.lower():
            print("Пароль не должен следовать простым шаблонам, таким как 'password123' или 'qwerty123'")
            return False
    return True

def register():
	global user_address
	password = ""
	while password == "":
		password = getpass('Введите пароль: ')
		if not is_strong_password(password):
			password = ""
	address = w3.geth.personal.new_account(password)
	print("Регистрация успешна! Ваш ключ:", address)
	user_address = address
	main()

def login():
	global user_address
	while True:
		try:
			address = getpass('Введите адрес, начиная с 0x: ')
			address_checksum = Web3.to_checksum_address(address)
			break
		except:
			print('Неверный формат адреса')
	password = getpass('Введите пароль: ')
	try:
		islogged = w3.geth.personal.unlock_account(address_checksum, password)
		user_address = address_checksum
		print('Успешный вход!')
	except Exception as e:
		print(f'Неверный адрес или пароль ({e})')
		main()
		return
	menu()

def addEstate():
	name = input('Введите название: ')
	while True:
		try:
			number = int(input('Введите ID недвижимости: '))
			break
		except ValueError:
			print('Ошибка: не число')
	address_info = input('Введите адрес имущества: ')
	estate_type = input('Введите тип имущества: ')
	while True:
		try:
			area = int(input('Введите площадь: '))
			contract.functions.AddEstate(name, number, address_info, estate_type, area).transact({'from': user_address})
			print('Успешно!')
			break
		except ContractLogicError as e:
			print(e.message)
			break
		except ValueError:
			print('Ошибка: не число')

def addAdvert():
	while True:
		try:
			estateId = int(input('Введите ID недвижимости: '))
			break
		except:
			print('Ошибка: не число')
	while True:
		try:
			price = int(input('Введите цену: '))
			break
		except:
			print('Ошибка: не число')
	currency = input('Введите тип валюты (wei, gwei, ether): ')
	try:
		contract.functions.AddAdvert(estateId, price, currency).transact({'from': user_address})
		print('Успешно')
	except ContractLogicError as e:
		print(e.message)

def changeEstateStatus():
	while True:
		try:
			estateId = int(input('Введите ID недвижимости: '))
			break
		except:
			print('Ошибка: не число')
	try:
		contract.functions.ChangeEstateStatus(estateId).transact({'from': user_address})
		print('Успешно!')
	except ContractLogicError as e:
		print(e.message)

def changeAdvertStatus():
	while True:
		try:
			estateId = int(input('Введите ID недвижимости: '))
			break
		except:
			print('Ошибка: не число')
	try:
		contract.functions.ChangeAdvertStatus(estateId).transact({'from': user_address})
		print('Успешно!')
	except ContractLogicError as e:
		print(e.message)

def withdraw():
	while True:
		try:
			amount = int(input('Введите цену: '))
			break
		except:
			print('Ошибка: не число')
	currency = input('Введите тип валюты (wei, gwei, ether): ')
	try:
		contract.functions.withdraw(amount, currency).transact({'from': user_address})
		print('Успешно!')
	except ContractLogicError as e:
		print(e.message)

def get_balance():
	try:
		balance = contract.functions.get_balance().call()
		print(f'Баланс: {balance}')
	except ContractLogicError as e:
		print(e.message)

def get_estates():
	try:
		estates = contract.functions.get_estates().call()
		for estate in estates:
			print('Владелец:', estate[0])
			print("Номер:", estate[1])
			print("Название:", estate[2])
			print("Адрес:", estate[3])
			print("Тип:", estate[4])
			print("Площадь:", estate[5])
			print("Доступна:", estate[6])
			print("--------")
	except ContractLogicError as e:
		print(e.message)

def get_adverts():
	try:
		adverts = contract.functions.get_adverts().call()
		for advert in adverts:
			estate = advert[0]
			print('Владелец:', estate[0])
			print("Номер:", estate[1])
			print("Название:", estate[2])
			print("Адрес:", estate[3])
			print("Тип:", estate[4])
			print("Площадь:", estate[5])
			print("Доступна:", estate[6])
			print("Цена:", advert[1])
			print("Валюта:", advert[2])
			print("Доступно:", advert[3])
			print("--------")
	except ContractLogicError as e:
		print(e.message)

def buy_estate():
	while True:
		try:
			estateId = int(input('Введите ID недвижимости: '))
			break
		except:
			print('Ошибка: не число')
	while True:
		try:
			value = int(input('Введите сумму, которую зачислить на счет: '))
			break
		except:
			print('Ошибка: не число')
	try:
		contract.functions.buy_estate(estateId).transact({'from': user_address, 'value': value}) # type: ignore
		print('Успешно!')
	except ContractLogicError as e:
		print(e.message)

def menu():
	while True:
		print('0. Выйти')
		print('1. Добавить недвижимость')
		print('2. Добавить объявление')
		print('3. Изменить статус недвижимости')
		print('4. Изменить статус объявления')
		print('5. Вывести средства')
		print('6. Узнать свой баланс')
		print('7. Получить список недвижимости')
		print('8. Получить список объявлений')
		print('9. Купить недвижимость')
		choice = int(input('Выберите: '))
		match choice:
			case 0:
				main()
				return
			case 1:
				addEstate()
			case 2:
				addAdvert()
			case 3:
				changeEstateStatus()
			case 4:
				changeAdvertStatus()
			case 5:
				withdraw()
			case 6:
				get_balance()
			case 7:
				get_estates()
			case 8:
				get_adverts()
			case 9:
				buy_estate()

def main():
    print('1. Вход')
    print('2. Регистрация')
    choice = int(input('Выберите действие: '))

    if choice == 1:
        login()
        pass
    elif choice == 2:
        register()

if __name__ == '__main__':
    main()