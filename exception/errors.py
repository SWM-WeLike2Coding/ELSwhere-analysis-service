from typing import List, Union


class ProductServiceServerException(Exception):
    def __init__(self, productIds: Union[int, List[int]]):
        if isinstance(productIds, int):
            self.productIdList = [productIds]
        elif isinstance(productIds, list):
            self.productIdList = productIds
        else:
            raise TypeError("productIds must be either an int or a list of ints")


class ValidateInitialBasePriceEvaluationDateException(Exception):
    def __init__(self, productId: int):
        self.productId = productId

class MonteCarloResultException(Exception):
    def __init__(self, productId: int):
        self.productId = productId

class AIResultException(Exception):
    def __init__(self, productId: int):
        self.productId = productId