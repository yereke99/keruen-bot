import PyPDF2

class PDFReaders:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
        self.reader = None

    def open_pdf(self):
        """Открываем PDF-файл для чтения."""
        self.file = open(self.file_path, 'rb')
        self.reader = PyPDF2.PdfReader(self.file)
    
    def close_pdf(self):
        """Закрываем PDF-файл."""
        if self.file:
            self.file.close()
    
    def get_number_of_pages(self):
        """Возвращает количество страниц в PDF-файле."""
        return len(self.reader.pages) if self.reader else 0
    
    def extract_text_from_page(self, page_num):
        """Извлекает текст с указанной страницы PDF."""
        if self.reader and page_num < len(self.reader.pages):
            page = self.reader.pages[page_num]
            return page.extract_text()
        return ""

    def determine_language(self):
        """Определяет язык PDF по ключевым словам на первой странице."""
        if self.reader:
            first_page_text = self.extract_text_from_page(0)
            if "Счет на оплату" in first_page_text or "Фискальный чек" in first_page_text:
                return 'russian'
            elif "Төлем шоты" in first_page_text or "Фискалдық түбіртек" in first_page_text:
                return 'kazakh'
            elif "Сатып алғаным" in first_page_text:
                return 'kazakh'
            elif "Покупки" in first_page_text:
                return 'russian'
        return 'unknown'
    
    def extract_detailed_info(self):
        """Извлекает каждую строку как отдельный элемент массива, учитывая ключевые слова на казахском и русском языках."""
        language = self.determine_language()
        
        # Определение ключевых слов в зависимости от языка
        if language == 'kazakh':
            specific_keywords = [
                "Фискалдық түбіртек", "ИП", "Төлем сәтті өтті", "₸", "Сату", "Фото и видео",
                "Түбіртек №", "QR", "Күні мен уақыты", "Төленді", "Мекенжай", 
                "Сатушының ЖСН/БСН", "Сатып алушының аты-жөні", "МТН", "МЗН", "ФБ", "ФДО"
            ]
        elif language == 'russian':
            specific_keywords = [
                "Фискальный чек", "ИП", "Платеж успешно совершен", "₸", "Продажа", "Фото и видео",
                "№ чека", "QR", "Дата и время", "Оплачено", "Адрес", 
                "ИИН/БИН продавца", "ФИО покупателя", "РНМ", "ЗНМ", "ФП", "ОФД"
            ]
        else:
            return ["Language not recognized."]

        # Извлечение строк, содержащих ключевые слова
        result_lines = []
        number_of_pages = self.get_number_of_pages()
        for page_num in range(number_of_pages):
            text = self.extract_text_from_page(page_num)
            if text:  # Проверяем, что текст не пустой
                lines = text.split('\n')
                for line in lines:
                    if any(keyword in line for keyword in specific_keywords):
                        result_lines.append(line.strip())  # Добавляем каждую строку отдельно
                        
        return result_lines

if __name__ == "__main__":
    # Инициализация PDFReader с путем к файлу
    pdf_reader = PDFReaders("/home/konditer/pdf/800703982_1730896380_15444790.pdf")

    # Открываем PDF для чтения
    pdf_reader.open_pdf()
    
    # Извлекаем детальную информацию
    detailed_info = pdf_reader.extract_detailed_info()
    print(detailed_info)  # Выводим результат в виде массива строк

    # Закрываем PDF после чтения
    pdf_reader.close_pdf()
