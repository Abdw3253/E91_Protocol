#pip install qiskit
#pip install qiskit-aer

from qiskit import QuantumCircuit, Aer, transpile, assemble, execute, IBMQ
from qiskit.visualization import plot_histogram

import numpy as np
import random
import math

import warnings
warnings.filterwarnings('ignore')


# Determine the amount of entanglement between these bits using the CHSH value
def entanglement_amount(alice_choices, alice_bits, bob_choices, bob_bits):
    
  # count the different measurement results
  # rows correspond to Alice and Bob's circuit choices: 00, 02, 20, 22
  # NOTE: We do not consider circuits 1 or 3 for this test
  # columns correspond to Alice and Bob's qubit measurements: 00, 01, 10, and 11
  circuits = {'00': 0, '02': 1, '20': 2, '22': 3}
  
  counts = [[0]*4 for i in range(4)]
  for i in range(len(alice_choices)):
    circuit = str(alice_choices[i]) + str(bob_choices[i])
    state = int(alice_bits[i]) + 2*int(bob_bits[i])

    if circuit in circuits: counts[circuits[circuit]][state] += 1


  # expectation values calculated by 
  # adding times Alice and Bob's bits agreed and
  # subtracting times Alice and Bob's bits disagreed
  expectations = []

  for circuit in range(4):
    expectations += [counts[circuit][0] + counts[circuit][3] - counts[circuit][1] - counts[circuit][2]]
    total = sum(counts[circuit])

    if total != 0: expectations[circuit] /= total


  # returning CHSH correlation
  return expectations[0] - expectations[1] + expectations[2] + expectations[3]
  

#========
# STEP 1: making 100 qubit for each Alice and Bob. Alice and Bob have alteranting qubits either 01 or 10.
#========
n = 100
alice_bob_qubits = []

for i in range(n):
  alice_bob_qubits += [QuantumCircuit(2, 2)]

  alice_bob_qubits[i].h(0)
  alice_bob_qubits[i].cx(0, 1)
  alice_bob_qubits[i].z(0)
  alice_bob_qubits[i].x(0)


#================
# EVE INTERCEPTS!: Eve is the haker here. It tries to measure the qubits and break their superposition.
# Try to make this step a comment and notice the difference.
#================
for i in range(n):
  alice_bob_qubits[i].measure([0, 1], [0, 1])

backend = Aer.get_backend('qasm_simulator')
job = execute(alice_bob_qubits, backend = backend, shots = 1)
result = job.result()
counts = result.get_counts()


eve_alice_bits = []
eve_bob_bits = []

for i in range(n):

  # Looks at measurement results
  bits = list(counts[i].keys())[0]
  eve_alice_bits += [bits[0]]
  eve_bob_bits += [bits[1]]

  # Prepares new qubits for Alice and Bob
  alice_bob_qubits[i] = QuantumCircuit(2, 2)

  # Makes sure they are in the same state she measured
  if eve_alice_bits[i] == 1: alice_bob_qubits[i].x(0)
  if eve_bob_bits[i] == 1: alice_bob_qubits[i].x(1)


#========
# Alice and Bob options
#========
alice_option_1 = QuantumCircuit(1, 1)
alice_option_1.h(0)
alice_option_1.measure(0, 0)

alice_option_2 = QuantumCircuit(1, 1)
alice_option_2.rz(math.pi/4,0)
alice_option_2.h(0)
alice_option_2.measure(0, 0)

alice_option_3 = QuantumCircuit(1, 1)
alice_option_3.rz(math.pi/2,0)
alice_option_3.h(0)
alice_option_3.measure(0, 0)

alice_options=[alice_option_1,alice_option_2,alice_option_3]


bob_option_1 = QuantumCircuit(1, 1)
bob_option_1.rz(math.pi/4,0)
bob_option_1.h(0)
bob_option_1.measure(0, 0)

bob_option_2 = QuantumCircuit(1,1)
bob_option_2.rz(math.pi/2,0)
bob_option_2.h(0)
bob_option_2.measure(0,0)

bob_option_3 = QuantumCircuit(1,1)
bob_option_3.rz(3*math.pi/4, 0)
bob_option_3.h(0)
bob_option_3.measure(0,0)

bob_options=[bob_option_1,bob_option_2,bob_option_3]
#========
# STEP2: Alice choose 100 random circuits and compose new circuit
#========
alice_choices = []
alice_circuits = []

for i in range(n):
  alice_choices += [random.randint(0, 2)]
  alice_bob_qubits[i] = alice_bob_qubits[i].compose(alice_options[alice_choices[i]], qubits = 0, clbits = 0)


#========
# STEP 3:Bob choose 100 random circuits and compose new circuit
#========
bob_choices = []
bob_circuits = []

for i in range(n):
  bob_choices += [random.randint(0, 2)]
  alice_bob_qubits[i] = alice_bob_qubits[i].compose(bob_options[bob_choices[i]], qubits = 1, clbits = 1)


#======================
# SIMULATE THE CIRCUIT
#======================
backend = Aer.get_backend('qasm_simulator')
job = execute(alice_bob_qubits, backend = backend, shots = 1)
result = job.result()
counts = result.get_counts()

alice_bits = []
bob_bits = []
for i in range(n):
  bits = list(counts[i].keys())[0]
  alice_bits += [bits[0]]
  bob_bits += [bits[1]]


#========
# STEP 4: checking the matching keys
#========
alice_key = []
alice_mismatched_choices = []
alice_mismatched_choice_bits = []

bob_key = []
bob_mismatched_choices = []
bob_mismatched_choice_bits = []

eve_key = []

for i in range(n):
  
  # MATCHING CHOICE
  if alice_options[alice_choices[i]] == bob_options[bob_choices[i]]:
    alice_key += [int(alice_bits[i])]
    bob_key += [1 - int(bob_bits[i])]
    eve_key += [int(eve_alice_bits[i])]

  # MISMATCHING CHOICE
  else:
    alice_mismatched_choices += [alice_choices[i]]
    bob_mismatched_choices += [bob_choices[i]]

    alice_mismatched_choice_bits += [alice_bits[i]]
    bob_mismatched_choice_bits += [bob_bits[i]]


entanglement = entanglement_amount(alice_mismatched_choices, alice_mismatched_choice_bits, bob_mismatched_choices, bob_mismatched_choice_bits)
print("Entanglement of Mismatched Choices: " + str(entanglement))
print("Alice's Key: " + str(alice_key))
print("Bob's Key: " + str(bob_key))
print("Eve's Key: " + str(eve_key))
print("Key Length: " + str(len(bob_key)))
print("Number of Disagreeing Key Bits between Alice and Bob: " + str(sum([alice_key[i] != bob_key[i] for i in range(len(alice_key))])))
print("Number of Disagreeing Key Bits between Alice and Eve: " + str(sum([alice_key[i] != eve_key[i] for i in range(len(alice_key))])))
print("Number of Disagreeing Key Bits between Bob and Eve: " + str(sum([bob_key[i] != eve_key[i] for i in range(len(alice_key))])))
