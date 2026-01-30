
from pipeline.controller import Pipeline
from programs import fibonacci

print("\n"+"="*50)
print("test 2: fibonacci")
print("="*50)

instructions = fibonacci.get_program()

pipeline = Pipeline(instructions)
pipeline.run()

print(f"\nvreau: x3=5")
print(f"am: x3={pipeline.registers.read(3)}")
print(f"status: {'OK' if pipeline.registers.read(3) == 5 else 'FAIL'}")
with open("teste/test_rez.txt", "w") as g:
    g.write(f"{pipeline.registers}\n")
    g.write(f"{pipeline.cycle-1} cicluri de ceas \n")
    if pipeline.registers.read(3) ==5:
        g.write(f"x3 este 5, cum trebuie")
    else:
        g.write(f"x3 este gresit, {pipeline.registers.read(3)}")