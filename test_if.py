from pipeline.controller import Pipeline
from programs import sum, fibonacci


print("="*50)
print("test 1: simple add")
print("="*50)

instructions = sum.get_program()
pipeline = Pipeline(instructions)
pipeline.run()

print(f"\nvreau: x3=8")
print(f"am: x3={pipeline.registers.read(3)}")
print(f"status: {'OK' if pipeline.registers.read(3) == 8 else 'FAIL'}")


print("\n\n" + "="*50)
print("test 2: fibonacci")
print("="*50)

instructions = fibonacci.get_program()
pipeline = Pipeline(instructions)
pipeline.run()

with open("test_rez.txt", "w") as g:
    if pipeline.registers.read(3) == 5:
        g.write(f"x3 este 5, cum trebuie")
    else:
        g.write(f"x3 este gresit, {pipeline.registers.read(3)}")

