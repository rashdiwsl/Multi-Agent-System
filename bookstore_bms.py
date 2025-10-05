# bookstore_bms.py
from owlready2 import *
import random
from mesa import Agent, Model
from mesa.time import RandomActivation   
import matplotlib.pyplot as plt

# -----------------------------
# 1. Ontology Setup
# -----------------------------
onto = get_ontology("http://test.org/bookstore.owl")

with onto:
    class Book(Thing):
        pass

    class Customer(Thing):
        pass

    class Employee(Thing):
        pass

    # Object Properties
    class purchases(Customer >> Book):
        pass

    # Data Properties
    class availableQuantity(DataProperty, FunctionalProperty):
        domain = [Book]
        range = [int]

    class hasPrice(DataProperty, FunctionalProperty):
        domain = [Book]
        range = [float]

# Add books to ontology
book1 = Book("b1")
book1.availableQuantity = 5
book1.hasPrice = 12.5

book2 = Book("b2")
book2.availableQuantity = 5
book2.hasPrice = 15.0

book3 = Book("b3")
book3.availableQuantity = 5
book3.hasPrice = 9.99

books = [book1, book2, book3]

# -----------------------------
# 2. SWRL Rules
# -----------------------------
# Rule 1: Customer purchase decreases quantity
try:
    rule1 = Imp()
    rule1.set_as_rule("""
        Customer(?c), Book(?b), purchases(?c, ?b), availableQuantity(?b, ?q) 
        -> availableQuantity(?b, ?q - 1)
    """)
    print("[SWRL] Purchase rule added successfully")
except Exception as e:
    print(f"[SWRL] Could not add purchase rule: {e}")

# Rule 2: Employee restocks if quantity < 2
try:
    rule2 = Imp()
    rule2.set_as_rule("""
        Employee(?e), Book(?b), availableQuantity(?b, ?q), swrlb:lessThan(?q, 2)
        -> availableQuantity(?b, ?q + 3)
    """)
    print("[SWRL] Restock rule added successfully")
except Exception as e:
    print(f"[SWRL] Could not add restock rule: {e}")

# -----------------------------
# 3. Mesa Agents
# -----------------------------
class CustomerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.purchased = []

    def step(self):
        book = random.choice(self.model.books)
        if book.availableQuantity > 0:
            book.availableQuantity -= 1
            self.purchased.append(book.name)

class EmployeeAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        for book in self.model.books:
            if book.availableQuantity < 2:
                book.availableQuantity += 3

# -----------------------------
# 4. Mesa Model
# -----------------------------
class BookstoreModel(Model):
    def __init__(self, num_customers=5, num_employees=2):
        self.schedule = RandomActivation(self)
        self.books = books

        # Add customers
        for i in range(num_customers):
            c = CustomerAgent(i, self)
            self.schedule.add(c)

        # Add employees
        for i in range(num_employees):
            e = EmployeeAgent(i + 100, self)
            self.schedule.add(e)

    def step(self):
        self.schedule.step()

# -----------------------------
# 5. Run Simulation
# -----------------------------
print("[Setup] Starting Bookstore MAS simulation.")
model = BookstoreModel(num_customers=8, num_employees=2)

for i in range(15):
    print(f"[Model] Step {i+1}/15 running...")
    model.step()

print("[Model] Simulation finished.")

# -----------------------------
# 6. Show Results
# -----------------------------
print("\nFinal inventory (ontology):")
for b in model.books:
    print(f" Book {b.name} | qty={b.availableQuantity} | price={b.hasPrice}")

print("\nCustomer purchases (ontology):")
for agent in model.schedule.agents:
    if isinstance(agent, CustomerAgent):
        print(f" Customer {agent.unique_id} purchased: {agent.purchased}")

# Save ontology
onto.save("bookstore_result.owl")
print("\nOntology saved to 'bookstore_result.owl'")

# Plot final inventory
fig, ax = plt.subplots()
book_names = [b.name for b in books]
quantities = [b.availableQuantity for b in books]
ax.bar(book_names, quantities)
ax.set_ylabel("Available Quantity")
ax.set_title("Final Inventory after Simulation")
plt.savefig("sales.png")
print("Sales plot saved to 'sales.png'")

# -----------------------------
# 7. Apply Reasoner
# -----------------------------
try:
    with onto:
        sync_reasoner()
    print("[Reasoner] Reasoner finished.")
except Exception as e:
    print(f"[Reasoner] Reasoner could not run: {e}")
