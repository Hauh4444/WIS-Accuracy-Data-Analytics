from PyInstaller.utils.hooks import collect_submodules


hiddenimports = [
    'reportlab.rl_config',
    'reportlab.pdfbase',
    'reportlab.pdfbase.ttfonts',
    'reportlab.pdfbase.cidfonts',
    'reportlab.pdfbase.pdfmetrics',
    'reportlab.pdfgen',
    'reportlab.graphics',
    'reportlab.graphics.shapes',
    'reportlab.graphics.charts',
    'reportlab.graphics.barcode.code39',
    'reportlab.graphics.barcode.code93',
    'reportlab.graphics.barcode.code128',
    'reportlab.graphics.barcode.eanbc',
    'reportlab.graphics.barcode.ecc200datamatrix',
    'reportlab.graphics.barcode.qr',
    'reportlab.graphics.barcode.usps',
    'reportlab.graphics.barcode.usps4s',
    'reportlab.graphics.barcode.rss',
    'reportlab.graphics.barcode.pdf417',
    'reportlab.graphics.barcode.codabar',
    'reportlab.graphics.barcode.i2of5',
    'reportlab.graphics.barcode.macro',
    'reportlab.graphics.barcode.util'
]