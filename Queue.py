class Node:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class Queue:
    def __init__(self):
        self.front = None
        self.back = None
        self.count = 0  # ✅ este sí lo usas para size()
        self.contador = 0  # ✅ para asignar número incremental

    def push(self, value):
        new_node = Node(value)
        if self.back is None:
            self.front = self.back = new_node
        else:
            self.back.next = new_node
            self.back = new_node
        self.count += 1

    def pop(self):
        if self.front is None:
            return None
        value = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.back = None
        self.count -= 1
        return value

    def peek(self):
        return self.front.data if self.front else None

    def is_empty(self):
        return self.front is None

    def size(self):
        return self.count

    def print(self):
        current = self.front
        while current:
            print(f"{current.data} -> ", end="")
            current = current.next
        print("None")
