from models import (Base, session,
                    Book, engine)
import datetime
import csv
import time


def menu():
    while True:
        print('''
            \nPROGRAMMING BOOKS
            \r1) Add book
            \r2) View all books
            \r3) Search for book
            \r4) Book Analysis
            \r5) Exit''')
        choice = input('Choose an option> ')
        if choice in ('1', '2', '3', '4', '5'):
            return choice
        else:
            input('''
                \rEnter a number from 1-5.
                \rPress enter to try again.''')


def sub_menu():
    while True:
        print('''
            \n1) Edit
            \r2) Delete
            \r3) Return to main menu''')
        choice = input('Choose an option> ')
        if choice in ('1', '2', '3'):
            return choice
        else:
            input('''
                \rEnter a number from 1-3.
                \rPress enter to try again.''')


def clean_date(date_str):
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    split_date = date_str.split(' ')
    try:
        month = int(months.index(split_date[0]) + 1)
        day = int(split_date[1].split(',')[0])
        year = int(split_date[2])
        return_date = datetime.date(year, month, day)
    except ValueError:
        input('''
        \n****** INVALID DATE FORMAT ******
        \rPress enter to try again.
        \r*********************************''')
        return
    else:
        return return_date


def clean_price(price_str):
    try:
        price_float = float(price_str)
        return_price = int(price_float * 100)
    except ValueError:
        input('''
        \n****** INVALID PRICE FORMAT ******
        \rPress enter to try again.
        \r*********************************''')
        return
    else:
        return return_price


def clean_choice(choice_str, id_options):
    try:
        if int(choice_str) in id_options:
            return_choice = int(choice_str)
        else:
            raise ValueError
    except ValueError:
        input('''
        \n****** INVALID CHOICE ***********
        \rPress enter to try again.
        \r*********************************''')
        return
    else:
        return return_choice


def edit_check(column_name, current_value):
    print(f'\n**** EDIT {column_name} ****')
    if column_name == 'Price':
        print(f'\rCurrent price: £{current_value / 100}')
    elif column_name == 'Date':
        print(f'\rCurrent date: {current_value.strftime("%B %d, %Y")}')
    else:
        print(f'\rCurrent value: {current_value}')

    if column_name == 'Date' or column_name == 'Price':
        while True:
            changes = input('What would you like to change the value to? ')
            if column_name == 'Date':
                changes = clean_date(changes)
                if type(changes) == datetime.date:
                    return changes
            elif column_name == 'Price':
                changes = clean_price(changes)
                if type(changes) == int:
                    return changes
    else:
        return input('What would you like to change the value to? ')


def add_csv():
    with open('suggested_books.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            book_in_db = session.query(Book).filter(Book.title == row[0]).one_or_none()
            if book_in_db == None:
                title = row[0]
                author = row[1]
                date = clean_date(row[2])
                price = clean_price(row[3])
                new_book = Book(title=title, author=author, published_date=date, price=price)
                session.add(new_book)
        session.commit()


def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == '1':
            # add book
            title = input('Title: ')
            author = input('Author: ')
            date = None
            while type(date) != datetime.date:
                date = input('Published date (Month dd, yyyy): ')
                date = clean_date(date)
            price = None
            while type(price) != int:
                price = input('Price (xx.yy): ')
                price = clean_price(price)
            new_book = Book(title=title, author=author, published_date=date, price=price)
            session.add(new_book)
            session.commit()
            print('Book added!')
            time.sleep(1.5)
        elif choice == '2':
            # view books
            for book in session.query(Book):
                print(f'{book.id} | {book.title} | {book.author}')
            input('\nPress enter to return to the main menu.')
        elif choice == '3':
            # search book
            id_options = []
            for book in session.query(Book):
                id_options.append(book.id)
            id_choice = None
            while type(id_choice) != int:
                id_choice = input(f'''
                    \nId Options: {id_options}
                    \rBookid: ''')
                id_choice = clean_choice(id_choice, id_options)
            my_book = session.query(Book).filter_by(id=id_choice).first()
            print(f'''
                \n"{my_book.title}" by {my_book.author}
                \rPublished: {my_book.published_date}
                \rPrice: £{my_book.price / 100}''')
            sub_choice = sub_menu()
            if sub_choice == '1':
                # edit
                print(f"'Title', {my_book.title}")
                my_book.title = edit_check('Title', my_book.title)
                my_book.author = edit_check('Author', my_book.author)
                my_book.published_date = edit_check('Date', my_book.published_date)
                my_book.price = edit_check('Price', my_book.price)
                session.commit()
                print('Book updated!')
                time.sleep(1.5)
            if sub_choice == '2':
                # delete
                session.delete(my_book)
                session.commit()
                print('Book deleted!')
                time.sleep(1.5)
        elif choice == '4':
            # analysis
            newest_book = session.query(Book).order_by(Book.published_date.desc()).first()
            oldest_book = session.query(Book).order_by(Book.published_date).first()
            total_books = session.query(Book).count()
            python_books = session.query(Book).filter(Book.title.like('%Python%')).count()
            expensive_book = session.query(Book).order_by(Book.price.desc()).first()
            print(f'''
                \n***** BOOK ANALYSIS *****
                \rOldest book: {oldest_book.published_date}
                \rNewest book: {newest_book.published_date}
                \rTotal books in database: {total_books}
                \rNumber of Python books: {python_books}
                \rMost expensive book: £{expensive_book.price / 100}
                \r*************************
            ''')
            input('Press enter to return to main menu.')
        else:
            print('GOODBYE')
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()

    # for book in session.query(Book):
    #    print(book)