from types import MethodType
from typing import List


class MethodCollection:
    queries: List[MethodType]
    mutations: List[MethodType]
    subscriptions: List[MethodType]

    def __init__(self):
        self.queries = []
        self.mutations = []
        self.subscriptions = []
