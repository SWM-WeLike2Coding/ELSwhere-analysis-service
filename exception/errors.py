class ProductServiceServerException(Exception):
    def __init__(self, productId: int):
        self.productId = productId