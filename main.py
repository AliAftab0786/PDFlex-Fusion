from utils import *

class PDFMergerApp(QWidget):
    def __init__(self):
        print("Initializing PDFMergerApp")
        super().__init__()
        self.initUI()
        self.pdf_files = []

    def initUI(self):
        print("Initializing UI")
        self.setWindowTitle('PDF Merger')
        
        layout = QVBoxLayout()

        self.fileListWidget = QListWidget()
        self.fileListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.fileListWidget)
        
        self.previewLabel = QLabel()
        layout.addWidget(self.previewLabel)
        
        selectButton = QPushButton('Select PDF Files')
        selectButton.clicked.connect(self.selectFiles)
        layout.addWidget(selectButton)

        previewButton = QPushButton('Preview Selected Page')
        previewButton.clicked.connect(self.previewPage)
        layout.addWidget(previewButton)
        
        mergeButton = QPushButton('Merge PDFs')
        mergeButton.clicked.connect(self.mergePDFs)
        layout.addWidget(mergeButton)

        self.setLayout(layout)
    
    def selectFiles(self):
        print("Selecting PDF Files")
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)", options=options)
        if files:
            self.pdf_files = files
            self.fileListWidget.addItems(files)
    
    def previewPage(self):
        print("Previewing Selected Page")
        selectedItems = self.fileListWidget.selectedItems()
        if not selectedItems:
            return
        selectedFile = selectedItems[0].text()
        pages = convert_from_path(selectedFile, 1)
        if pages:
            page = pages[0]
            page.save('temp_preview.png')
            self.previewLabel.setPixmap(QPixmap('temp_preview.png'))
            os.remove('temp_preview.png')

    def mergePDFs(self):
        print("----------------------------------------")
        print("Merging PDFs")
        print("----------------------------------------")
        output = PdfWriter()
        output_pdf_path = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")[0]
        if not output_pdf_path:
            return

        page_counter = 0
        total_pages = 0
        file_page_counts = {}

        # First pass to get total page count
        for pdf_file in self.pdf_files:
            pdf = PdfReader(open(pdf_file, 'rb'))
            num_pages = len(pdf.pages)
            file_page_counts[pdf_file] = num_pages
            total_pages += num_pages

        # Second pass to add pages with headers
        for pdf_file in self.pdf_files:
            pdf = PdfReader(open(pdf_file, 'rb'))
            num_pages = len(pdf.pages)
            for i in range(num_pages):
                page = pdf.pages[i]
                page_counter += 1

                # Add header
                header = f"{os.path.basename(pdf_file)} - p.{i + 1} of {num_pages} - Total p.{page_counter} of {total_pages}"
                self.add_header(page, header, width=int(page.mediabox.width), height=int(page.mediabox.height))
                
                output.add_page(page)

        with open(output_pdf_path, 'wb') as output_stream:
            output.write(output_stream)
        print("-------------------------------------------------------")
        print("PDFs merged successfully!")
        print("-------------------------------------------------------")
    def add_header(self, page, header_text, width, height):
        # Create a temporary PDF with the header text using ReportLab
        c = canvas.Canvas("temp_header.pdf", pagesize=(width, height))
        c.setFont("Helvetica", 12)
        c.drawString(10, height - 30, header_text)
        c.save()

        # Read the temporary PDF and merge it with the current page
        header_pdf = PdfReader("temp_header.pdf")
        header_page = header_pdf.pages[0]

        page.merge_page(header_page)
        os.remove("temp_header.pdf")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFMergerApp()
    ex.show()
    sys.exit(app.exec_())
