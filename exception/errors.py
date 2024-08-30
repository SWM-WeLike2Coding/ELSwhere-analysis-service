from typing import List, Union

class ProductServiceServerException(Exception):
    def __init__(self, productIds: Union[int, List[int]]):
        if isinstance(productIds, int):
            self.productIdList = [productIds]
        elif isinstance(productIds, list):
            self.productIdList = productIds
        else:
            raise TypeError("productIds must be either an int or a list of ints")