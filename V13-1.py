from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QDialogButtonBox, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QDialog, QGroupBox, QHBoxLayout, QRadioButton, QCheckBox, QDialogButtonBox
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    isbn = Column(String)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    publication_year = Column(Integer)
    page_count = Column(Integer)
    genre = Column(String)
    status = Column(String)

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    membership_type = Column(String)
    registration_date = Column(Date)
    contact_info = Column(String)

class Lending(Base):
    __tablename__ = 'lendings'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    member_id = Column(Integer, ForeignKey('members.id'))
    lending_date = Column(Date)
    return_date = Column(Date)
    returned = Column(Integer, default=0)

class LibraryManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_database()
        self.setGeometry(100, 100, 800, 600)
        self.book_id_input = QLineEdit()
        self.member_id_input = QLineEdit()
        self.init_ui()

    def init_database(self):
        engine = create_engine("sqlite:///library.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.default_data()

    def default_data(self):
        if not self.session.query(Book).count():
            self.session.add_all([
                Book(isbn='123456789', title='Example Book 1', author='John Doe', publisher='Publisher A',
                     publication_year=2020, page_count=200, genre='Fiction', status='Mevcut'),
                Book(isbn='987654321', title='Example Book 2', author='Jane Smith', publisher='Publisher B',
                     publication_year=2018, page_count=250, genre='Science', status='Mevcut')
            ])
        if not self.session.query(Member).count():
            self.session.add_all([
                Member(full_name='Alice Brown', membership_type='Standart', registration_date=datetime.now().date(),
                       contact_info='alice@example.com'),
                Member(full_name='Bob Green', membership_type='Premium', registration_date=datetime.now().date(),
                       contact_info='bob@example.com')
            ])
        self.session.commit()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.init_search_tab()
        self.init_book_management_tab()
        self.init_membership_tab()
        self.init_lending_tab()
        self.init_book_list_tab()
        self.init_member_list_tab()
        self.init_lending_list_tab()

    def init_search_tab(self):
        self.tab_search = QWidget()
        layout = QVBoxLayout(self.tab_search)
        self.tabs.addTab(self.tab_search, "Kitap Ara")
        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)
        self.search_button = QPushButton("Ara")
        layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.search_books)

        self.filter_group = QGroupBox("Filtrele")
        filter_layout = QHBoxLayout(self.filter_group)
        self.filter_group.setLayout(filter_layout)
        self.filter_by_status = QComboBox()
        self.filter_by_status.addItems(["Tüm Kitaplar", "Mevcut", "Kiralık"])
        filter_layout.addWidget(self.filter_by_status)
        self.filter_button = QPushButton("Filtrele")
        filter_layout.addWidget(self.filter_button)
        layout.addWidget(self.filter_group)

    def search_books(self):
        search_term = self.search_input.text().lower()
        status = self.filter_by_status.currentText()
        if status == "Tüm Kitaplar":
            books = self.session.query(Book).filter(
                Book.title.like(f"%{search_term}%") |
                Book.author.like(f"%{search_term}%") |
                Book.publisher.like(f"%{search_term}%") |
                Book.genre.like(f"%{search_term}%")
            ).all()
        elif status == "Mevcut":
            books = self.session.query(Book).filter_by(status='Mevcut').filter(
                Book.title.like(f"%{search_term}%") |
                Book.author.like(f"%{search_term}%") |
                Book.publisher.like(f"%{search_term}%") |
                Book.genre.like(f"%{search_term}%")
            ).all()
        else:
            books = self.session.query(Book).filter_by(status='Kiralık').filter(
                Book.title.like(f"%{search_term}%") |
                Book.author.like(f"%{search_term}%") |
                Book.publisher.like(f"%{search_term}%") |
                Book.genre.like(f"%{search_term}%")
            ).all()

        dialog = BookSearchDialog(books)
        dialog.exec_()

    def filter_books(self):
        status = self.filter_by_status.currentText()
        if status == "Tüm Kitaplar":
            books = self.session.query(Book).all()
        elif status == "Mevcut":
            books = self.session.query(Book).filter_by(status='Mevcut').all()
        else:
            books = self.session.query(Book).filter_by(status='Kiralık').all()

        dialog = BookFilterDialog(books)
        dialog.exec_()

    def init_book_management_tab(self):
        self.tab_book_management = QWidget()
        layout = QVBoxLayout(self.tab_book_management)
        self.tabs.addTab(self.tab_book_management, "Kitap İşlemleri")
        self.book_operations_menu = QTabWidget()
        layout.addWidget(self.book_operations_menu)
        self.init_add_book_tab()
        self.init_edit_book_tab()
        self.init_delete_book_tab()

    def init_add_book_tab(self):
        self.tab_add_book = QWidget()
        layout = QFormLayout(self.tab_add_book)
        self.book_operations_menu.addTab(self.tab_add_book, "Kitap Ekle")
        self.isbn_input = QLineEdit()
        layout.addRow("ISBN:", self.isbn_input)
        self.title_input = QLineEdit()
        layout.addRow("Kitap Adı:", self.title_input)
        self.author_input = QLineEdit()
        layout.addRow("Yazar:", self.author_input)
        self.publisher_input = QLineEdit()
        layout.addRow("Yayınevi:", self.publisher_input)
        self.publication_year_input = QLineEdit()
        layout.addRow("Basım Yılı:", self.publication_year_input)
        self.page_count_input = QLineEdit()
        layout.addRow("Sayfa Sayısı:", self.page_count_input)
        self.genre_input = QLineEdit()
        layout.addRow("Tür:", self.genre_input)
        self.status_input = QComboBox()
        self.status_input.addItems(["Mevcut", "Kiralık"])
        layout.addRow("Durum:", self.status_input)
        self.add_book_button = QPushButton("Kitap Ekle")
        layout.addRow(self.add_book_button)
        self.add_book_button.clicked.connect(self.add_book)

    def add_book(self):
        isbn = self.isbn_input.text()
        title = self.title_input.text()
        author = self.author_input.text()
        publisher = self.publisher_input.text()
        publication_year = int(self.publication_year_input.text())
        page_count = int(self.page_count_input.text())
        genre = self.genre_input.text()
        status = self.status_input.currentText()

        if not isbn or not title or not author or not publisher or not publication_year or not page_count or not genre or not status:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        if self.session.query(Book).filter_by(isbn=isbn).first():
            QMessageBox.warning(self, "Hata", "Bu ISBN numarası zaten mevcut.")
            return

        new_book = Book(isbn=isbn, title=title, author=author, publisher=publisher,
                        publication_year=publication_year, page_count=page_count, genre=genre, status=status)
        self.session.add(new_book)
        self.session.commit()
        self.refresh_lists()

    def init_edit_book_tab(self):
        self.tab_edit_book = QWidget()
        layout = QFormLayout(self.tab_edit_book)
        self.book_operations_menu.addTab(self.tab_edit_book, "Kitap Düzenle")
        self.book_id_input_edit = QLineEdit()
        layout.addRow("Kitap ID:", self.book_id_input_edit)
        self.isbn_input_edit = QLineEdit()
        layout.addRow("ISBN:", self.isbn_input_edit)
        self.title_input_edit = QLineEdit()
        layout.addRow("Kitap Adı:", self.title_input_edit)
        self.author_input_edit = QLineEdit()
        layout.addRow("Yazar:", self.author_input_edit)
        self.publisher_input_edit = QLineEdit()
        layout.addRow("Yayınevi:", self.publisher_input_edit)
        self.publication_year_input_edit = QLineEdit()
        layout.addRow("Basım Yılı:", self.publication_year_input_edit)
        self.page_count_input_edit = QLineEdit()
        layout.addRow("Sayfa Sayısı:", self.page_count_input_edit)
        self.genre_input_edit = QLineEdit()
        layout.addRow("Tür:", self.genre_input_edit)
        self.status_input_edit = QComboBox()
        self.status_input_edit.addItems(["Mevcut", "Kiralık"])
        layout.addRow("Durum:", self.status_input_edit)
        self.edit_book_button = QPushButton("Kitap Düzenle")
        layout.addRow(self.edit_book_button)
        self.edit_book_button.clicked.connect(self.edit_book)

    def edit_book(self):
        book_id = self.book_id_input_edit.text()
        isbn = self.isbn_input_edit.text()
        title = self.title_input_edit.text()
        author = self.author_input_edit.text()
        publisher = self.publisher_input_edit.text()
        publication_year = int(self.publication_year_input_edit.text())
        page_count = int(self.page_count_input_edit.text())
        genre = self.genre_input_edit.text()
        status = self.status_input_edit.currentText()

        if not isbn or not title or not author or not publisher or not publication_year or not page_count or not genre or not status:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            QMessageBox.warning(self, "Hata", "Bu kitap bulunamadı.")
            return

        book.isbn = isbn
        book.title = title
        book.author = author
        book.publisher = publisher
        book.publication_year = publication_year
        book.page_count = page_count
        book.genre = genre
        book.status = status
        self.session.commit()
        self.refresh_lists()

    def init_delete_book_tab(self):
        self.tab_delete_book = QWidget()
        layout = QVBoxLayout(self.tab_delete_book)
        self.book_operations_menu.addTab(self.tab_delete_book, "Kitap Sil")
        self.book_id_input_delete = QLineEdit()
        layout.addWidget(QLabel("Silmek istediğiniz kitabın ID'sini giriniz:"))
        layout.addWidget(self.book_id_input_delete)
        self.delete_book_button = QPushButton("Kitap Sil")
        layout.addWidget(self.delete_book_button)
        self.delete_book_button.clicked.connect(self.delete_book)

    def delete_book(self):
        book_id = self.book_id_input_delete.text()

        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            QMessageBox.warning(self, "Hata", "Bu kitap bulunamadı.")
            return

        lendings = self.session.query(Lending).filter_by(book_id=book_id).all()
        if lendings:
            QMessageBox.warning(self, "Hata", "Bu kitap ödünç verilmiş, silinemez.")
            return

        self.session.delete(book)
        self.session.commit()
        self.refresh_lists()

    def init_membership_tab(self):
        self.tab_membership = QWidget()
        layout = QVBoxLayout(self.tab_membership)
        self.tabs.addTab(self.tab_membership, "Üyelik İşlemleri")
        self.sub_tabs = QTabWidget()
        layout.addWidget(self.sub_tabs)
        self.init_add_member_tab()
        self.init_edit_member_tab()
        self.init_delete_member_tab()

    def init_add_member_tab(self):
        self.tab_add_member = QWidget()
        layout = QFormLayout(self.tab_add_member)
        self.sub_tabs.addTab(self.tab_add_member, "Üye Ekle")
        self.full_name_input = QLineEdit()
        layout.addRow("Ad Soyad:", self.full_name_input)
        self.membership_type_input = QComboBox()
        self.membership_type_input.addItems(["Standart", "Premium"])
        layout.addRow("Üyelik Türü:", self.membership_type_input)
        self.registration_date_input = QDateEdit()
        self.registration_date_input.setDate(datetime.now().date())
        layout.addRow("Kayıt Tarihi:", self.registration_date_input)
        self.contact_info_input = QLineEdit()
        layout.addRow("İletişim Bilgileri:", self.contact_info_input)
        self.add_member_button = QPushButton("Üye Ekle")
        layout.addRow(self.add_member_button)
        self.add_member_button.clicked.connect(self.add_member)

    def add_member(self):
        full_name = self.full_name_input.text()
        membership_type = self.membership_type_input.currentText()
        registration_date = self.registration_date_input.date().toPyDate()
        contact_info = self.contact_info_input.text()

        if not full_name or not membership_type or not registration_date or not contact_info:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        new_member = Member(full_name=full_name, membership_type=membership_type, registration_date=registration_date, contact_info=contact_info)
        self.session.add(new_member)
        self.session.commit()
        self.refresh_lists()

    def init_edit_member_tab(self):
        self.tab_edit_member = QWidget()
        layout = QFormLayout(self.tab_edit_member)
        self.sub_tabs.addTab(self.tab_edit_member, "Üye Düzenle")
        self.member_id_input_edit = QLineEdit()
        layout.addRow("Üye ID:", self.member_id_input_edit)
        self.full_name_input_edit = QLineEdit()
        layout.addRow("Ad Soyad:", self.full_name_input_edit)
        self.membership_type_input_edit = QComboBox()
        self.membership_type_input_edit.addItems(["Standart", "Premium"])
        layout.addRow("Üyelik Türü:", self.membership_type_input_edit)
        self.registration_date_input_edit = QDateEdit()
        self.registration_date_input_edit.setDate(datetime.now().date())
        layout.addRow("Kayıt Tarihi:", self.registration_date_input_edit)
        self.contact_info_input_edit = QLineEdit()
        layout.addRow("İletişim Bilgileri:", self.contact_info_input_edit)
        self.edit_member_button = QPushButton("Üye Düzenle")
        layout.addRow(self.edit_member_button)
        self.edit_member_button.clicked.connect(self.edit_member)

    def edit_member(self):
        member_id = self.member_id_input_edit.text()
        full_name = self.full_name_input_edit.text()
        membership_type = self.membership_type_input_edit.currentText()
        registration_date = self.registration_date_input_edit.date().toPyDate()
        contact_info = self.contact_info_input_edit.text()

        if not full_name or not membership_type or not registration_date or not contact_info:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        member = self.session.query(Member).filter_by(id=member_id).first()
        if not member:
            QMessageBox.warning(self, "Hata", "Bu üye bulunamadı.")
            return

        member.full_name = full_name
        member.membership_type = membership_type
        member.registration_date = registration_date
        member.contact_info = contact_info
        self.session.commit()
        self.refresh_lists()

    def init_delete_member_tab(self):
        self.tab_delete_member = QWidget()
        layout = QVBoxLayout(self.tab_delete_member)
        self.sub_tabs.addTab(self.tab_delete_member, "Üye Sil")
        self.member_id_input_delete = QLineEdit()
        layout.addWidget(QLabel("Silmek istediğiniz üyenin ID'sini giriniz:"))
        layout.addWidget(self.member_id_input_delete)
        self.delete_member_button = QPushButton("Üye Sil")
        layout.addWidget(self.delete_member_button)
        self.delete_member_button.clicked.connect(self.delete_member)

    def delete_member(self):
        member_id = self.member_id_input_delete.text()

        member = self.session.query(Member).filter_by(id=member_id).first()
        if not member:
            QMessageBox.warning(self, "Hata", "Bu üye bulunamadı.")
            return

        lendings = self.session.query(Lending).filter_by(member_id=member_id).all()
        if lendings:
            QMessageBox.warning(self, "Hata", "Bu üye ödünç verilmiş kitapların var, silinemez.")
            return

        self.session.delete(member)
        self.session.commit()
        self.refresh_lists()

    def init_lending_tab(self):
        self.tab_lending = QWidget()
        layout = QVBoxLayout(self.tab_lending)
        self.tabs.addTab(self.tab_lending, "Ödünç İşlemleri")
        self.book_id_input = QLineEdit()
        layout.addWidget(QLabel("Kitap ID:"))
        layout.addWidget(self.book_id_input)
        self.member_id_input = QLineEdit()
        layout.addWidget(QLabel("Üye ID:"))
        layout.addWidget(self.member_id_input)
        self.lending_date_input = QDateEdit()
        self.lending_date_input.setDate(datetime.now().date())
        layout.addWidget(QLabel("Ödünç Tarihi:"))
        layout.addWidget(self.lending_date_input)
        self.return_date_input = QDateEdit()
        self.return_date_input.setDate(datetime.now().date())
        layout.addWidget(QLabel("Teslim Tarihi:"))
        layout.addWidget(self.return_date_input)
        self.lend_book_button = QPushButton("Kitap Ödünç Ver")
        layout.addWidget(self.lend_book_button)
        self.lend_book_button.clicked.connect(self.lend_book)

        self.return_button = QPushButton("İade Et")
        self.return_button.clicked.connect(self.return_lending)
        layout.addWidget(self.return_button)

        self.overdue_books_button = QPushButton("Geçmiş Ödünçler")
        layout.addWidget(self.overdue_books_button)
        self.overdue_books_button.clicked.connect(self.display_overdue_books)

        self.most_borrowed_button = QPushButton("En Çok Ödünç Alınan Kitaplar")
        layout.addWidget(self.most_borrowed_button)
        self.most_borrowed_button.clicked.connect(self.display_most_borrowed_books)

        self.least_borrowed_button = QPushButton("En Az Ödünç Alınan Kitaplar")
        layout.addWidget(self.least_borrowed_button)
        self.least_borrowed_button.clicked.connect(self.display_least_borrowed_books)

    def lend_book(self):
        try:
            book_id_input_text = self.book_id_input.text()
            if not book_id_input_text:
                QMessageBox.warning(self, "Uyarı", "Lütfen kitap ID'sini girin.")
                return

            book_id = int(book_id_input_text)
            member_id_input_text = self.member_id_input.text()
            if not member_id_input_text:
                QMessageBox.warning(self, "Uyarı", "Lütfen üye ID'sini girin.")
                return

            member_id = int(member_id_input_text)
            lending_date = self.lending_date_input.date().toPyDate()
            return_date = self.return_date_input.date().toPyDate()

            if lending_date >= return_date:
                QMessageBox.warning(self, "Uyarı", "Teslim tarihi ödünç tarihinden önce olamaz.")
                return

            book = self.session.query(Book).filter_by(id=book_id).first()
            if not book:
                QMessageBox.critical(self, "Hata", "Bu kitap bulunamadı.")
                return

            member = self.session.query(Member).filter_by(id=member_id).first()
            if not member:
                QMessageBox.critical(self, "Hata", "Bu üye bulunamadı.")
                return

            if book.status != 'Mevcut':
                QMessageBox.warning(self, "Uyarı", "Bu kitap şu anda müsait değil.")
                return

            new_lending = Lending(book_id=book_id, member_id=member_id, lending_date=lending_date, return_date=return_date)
            self.session.add(new_lending)
            self.session.commit()

            book.status = 'Kiralık'
            self.session.commit()

            self.refresh_lists()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmedik bir hata oluştu: {str(e)}")

    def return_book(self):
        book_id_input_text = self.book_id_input.text()
        if not book_id_input_text:
            QMessageBox.warning(self, "Hata", "Lütfen kitap ID'sini girin.")
            return

        book_id = int(book_id_input_text)
        member_id = int(self.member_id_input.text())

        book = self.session.query(Book).filter_by(id=book_id).first()
        if not book:
            QMessageBox.warning(self, "Hata", "Bu kitap bulunamadı.")
            return

        member = self.session.query(Member).filter_by(id=member_id).first()
        if not member:
            QMessageBox.warning(self, "Hata", "Bu üye bulunamadı.")
            return

        lendings = self.session.query(Lending).filter_by(book_id=book_id, member_id=member_id).all()
        if not lendings:
            QMessageBox.warning(self, "Hata", "Bu kitap bu üyeye ödünç verilmemiş.")
            return

        for lending in lendings:
            lending.returned = 1
            self.session.commit()

        self.session.delete(lending)  # <--- Add this line to remove the lending from the list
        self.session.commit()

        book.status = 'Mevcut'
        self.session.commit()

        self.refresh_lists()

    def display_overdue_books(self):
        lendings = self.session.query(Lending).filter(Lending.returned == False).all()
        dialog = OverdueBooksDialog(self.session, lendings)
        dialog.exec_()

    def init_book_list_tab(self):
        self.tab_book_list = QWidget()
        layout = QVBoxLayout(self.tab_book_list)
        self.tabs.addTab(self.tab_book_list, "Kitap Listesi")
        self.book_table = QTableWidget()
        layout.addWidget(self.book_table)
        self.refresh_book_list()

    def refresh_book_list(self):
        books = self.session.query(Book).all()
        self.display_books(books)

    def display_books(self, books):
        self.book_table.setRowCount(len(books))
        self.book_table.setColumnCount(8)
        self.book_table.setHorizontalHeaderLabels(['ID', 'ISBN', 'Kitap Adı', 'Yazar', 'Yayınevi', 'Basım Yılı',
                                                    'Sayfa Sayısı', 'Tür', 'Durum'])
        for i, book in enumerate(books):
            self.book_table.setItem(i, 0, QTableWidgetItem(str(book.id)))
            self.book_table.setItem(i, 1, QTableWidgetItem(book.isbn))
            self.book_table.setItem(i, 2, QTableWidgetItem(book.title))
            self.book_table.setItem(i, 3, QTableWidgetItem(book.author))
            self.book_table.setItem(i, 4, QTableWidgetItem(book.publisher))
            self.book_table.setItem(i, 5, QTableWidgetItem(str(book.publication_year)))
            self.book_table.setItem(i, 6, QTableWidgetItem(str(book.page_count)))
            self.book_table.setItem(i, 7, QTableWidgetItem(book.genre))
            self.book_table.setItem(i, 8, QTableWidgetItem(book.status))

    def init_member_list_tab(self):
        self.tab_member_list = QWidget()
        layout = QVBoxLayout(self.tab_member_list)
        self.tabs.addTab(self.tab_member_list, "Üye Listesi")
        self.member_table = QTableWidget()
        layout.addWidget(self.member_table)
        self.refresh_member_list()

    def refresh_member_list(self):
        members = self.session.query(Member).all()
        self.display_members(members)

    def display_members(self, members):
        self.member_table.setRowCount(len(members))
        self.member_table.setColumnCount(5)
        self.member_table.setHorizontalHeaderLabels(['ID', 'Ad Soyad', 'Üyelik Türü', 'Kayıt Tarihi', 'İletişim Bilgileri'])
        for i, member in enumerate(members):
            self.member_table.setItem(i, 0, QTableWidgetItem(str(member.id)))
            self.member_table.setItem(i, 1, QTableWidgetItem(member.full_name))
            self.member_table.setItem(i, 2, QTableWidgetItem(member.membership_type))
            self.member_table.setItem(i, 3, QTableWidgetItem(member.registration_date.strftime('%Y-%m-%d')))
            self.member_table.setItem(i, 4, QTableWidgetItem(member.contact_info))

    def init_lending_list_tab(self):
        self.tab_lending_list = QWidget()
        layout = QVBoxLayout(self.tab_lending_list)
        self.tabs.addTab(self.tab_lending_list, "Ödünç Verilen Kitaplar")
        self.lending_table = QTableWidget()
        self.lending_table.setColumnCount(6)
        self.lending_table.setHorizontalHeaderLabels(
            ["ID", "Kitap ID", "Üye ID", "Ödünç Tarihi", "Teslim Tarihi", "Durum"])
        layout.addWidget(self.lending_table)
        self.refresh_lending_list()

        # Buton iade et butonu ekleniyor
        self.return_button = QPushButton("İade Et")
        self.return_button.clicked.connect(self.show_return_dialog)
        layout.addWidget(self.return_button)
        
    def show_return_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("İade Et")
        layout = QVBoxLayout(dialog)

        book_id_label = QLabel("Kitap ID:")
        self.book_id_input = QLineEdit()
        layout.addWidget(book_id_label)
        layout.addWidget(self.book_id_input)

        member_id_label = QLabel("Üye ID:")
        self.member_id_input = QLineEdit()
        layout.addWidget(member_id_label)
        layout.addWidget(self.member_id_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            book_id = int(self.book_id_input.text())
            member_id = int(self.member_id_input.text())

            book = self.session.query(Book).filter_by(id=book_id).first()
            if not book:
                QMessageBox.warning(self, "Hata", "Bu kitap bulunamadı.")
                return

            member = self.session.query(Member).filter_by(id=member_id).first()
            if not member:
                QMessageBox.warning(self, "Hata", "Bu üye bulunamadı.")
                return

            lendings = self.session.query(Lending).filter_by(book_id=book_id, member_id=member_id, returned=0).all()
            if not lendings:
                QMessageBox.warning(self, "Hata", "Bu kitap bu üyeye ait iade edilmemiş ödünç bulunamadı.")
                return

            for lending in lendings:
                lending.returned = 1
                self.session.commit()

            self.session.commit() 

            book.status = 'Mevcut'
            self.session.commit()

            self.refresh_lending_list()

    def refresh_lending_list(self):
        lendings = self.session.query(Lending).filter(Lending.returned == False).all()
        self.display_lendings(lendings)

    def display_lendings(self, lendings):
        self.lending_table.setRowCount(0)
        for lending in lendings:
            row_position = self.lending_table.rowCount()
            self.lending_table.insertRow(row_position)
            self.lending_table.setItem(row_position, 0, QTableWidgetItem(str(lending.id)))
            self.lending_table.setItem(row_position, 1, QTableWidgetItem(str(lending.book_id)))
            self.lending_table.setItem(row_position, 2, QTableWidgetItem(str(lending.member_id)))
            self.lending_table.setItem(row_position, 3, QTableWidgetItem(str(lending.lending_date)))
            self.lending_table.setItem(row_position, 4, QTableWidgetItem(str(lending.return_date)))
            returned_value = bool(lending.returned)
            self.lending_table.setItem(row_position, 5, QTableWidgetItem(str(int(lending.returned))))

    def return_lending(self):
        selected_row = self.lending_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen iade etmek istediğiniz ödünçü seçin.")
            return

        lending_id = self.lending_table.item(selected_row, 0).text()
        lending = self.session.query(Lending).filter_by(id=int(lending_id)).first()
        if not lending:
            QMessageBox.warning(self, "Hata", "Bu ödünç bulunamadı.")
            return

        if lending.returned:
            QMessageBox.warning(self, "Hata", "Bu ödünç zaten iadede.")
            return

        book = self.session.query(Book).filter_by(id=lending.book_id).first()
        if not book:
            QMessageBox.warning(self, "Hata", "Bu kitap bulunamadı.")
            return

        book.status = 'Mevcut'
        lending.returned = True
        self.session.commit()

        self.lending_table.removeRow(selected_row)
        self.refresh_lists()

    def count_lendings_per_book(self):
        lendings_per_book = {}
        lendings = self.session.query(Lending).all()
        for lending in lendings:
            book_id = lending.book_id
            if book_id not in lendings_per_book:
                lendings_per_book[book_id] = 0
            lendings_per_book[book_id] += 1
        return lendings_per_book

    def display_most_borrowed_books(self):
        lendings_per_book = self.count_lendings_per_book()
        sorted_lendings = sorted(lendings_per_book.items(), key=lambda x: x[1], reverse=True)

        books_info = []
        for book_id, count in sorted_lendings:
            book = self.session.query(Book).filter_by(id=book_id).first()
            books_info.append(f"{book.title} - Ödünç Sayısı: {count}")

        QMessageBox.information(self, "En Çok Ödünç Alınan Kitaplar", "\n".join(books_info))

    def display_least_borrowed_books(self):
        lendings_per_book = self.count_lendings_per_book()
        sorted_lendings = sorted(lendings_per_book.items(), key=lambda x: x[1])

        books_info = []
        for book_id, count in sorted_lendings:
            book = self.session.query(Book).filter_by(id=book_id).first()
            books_info.append(f"{book.title} - Ödünç Sayısı: {count}")

        QMessageBox.information(self, "En Az Ödünç Alınan Kitaplar", "\n".join(books_info))
        
    def refresh_lists(self):
        self.refresh_book_list()
        self.refresh_member_list()
        self.refresh_lending_list()

class BookSearchDialog(QDialog):
    def __init__(self, books):
        super().__init__()

        self.setWindowTitle("Arama Sonuçları")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        if not books:
            layout.addWidget(QLabel("Arama sonucunda hiçbir kitap bulunamadı."))
        else:
            for book in books:
                book_info = f"İsim: {book.title}\nYazar: {book.author}\nYayınevi: {book.publisher}\nTür: {book.genre}\nDurum: {book.status}"
                layout.addWidget(QLabel(book_info))

        self.setLayout(layout)

class BookFilterDialog(QDialog):
    def __init__(self, books):
        super().__init__()

        self.setWindowTitle("Kitap Filtreleme")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        if not books:
            layout.addWidget(QLabel("Filtreleme sonucunda hiçbir kitap bulunamadı."))
        else:
            for book in books:
                book_info = f"ID: {book.id}\nİsim: {book.title}\nYazar: {book.author}\nYayınevi: {book.publisher}\nTür: {book.genre}\nDurum: {book.status}"
                layout.addWidget(QLabel(book_info))

        self.setLayout(layout)

class OverdueBooksDialog(QtWidgets.QDialog):
    def __init__(self, session, lendings, parent=None):
        super().__init__(parent)
        self.session = session

        self.setWindowTitle("Geçmiş Ödünçler")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        if not lendings:
            layout.addWidget(QLabel("Geçmiş ödünç verilen kitap bulunamadı."))
        else:
            for lending in lendings:
                book = self.session.query(Book).filter_by(id=lending.book_id).first()
                lending_info = f"Kitap ID: {lending.book_id}\nKitap İsim: {book.title}\nÜye ID: {lending.member_id}\nÖdünç Tarihi: {lending.lending_date}\nTeslim Tarihi: {lending.return_date}"
                layout.addWidget(QLabel(lending_info))

        self.setLayout(layout)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LibraryManagement()
    window.show()
    sys.exit(app.exec_())