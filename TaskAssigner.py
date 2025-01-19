import utils as ut

import pandas as pd
import random

# Example list of possible people
people = ["Viktor", "Frank", "Firale", "Eva", "Florian"]

# Read the CSV file
df = pd.read_csv("sp500_classifications2.csv")


# Keep only rows that are not 'Unclassified'
df = df[df["Classification"] != "Unclassified"]

# Assign each row to a person in round-robin fashion
df["AssignedPerson"] = [people[i % len(people)] for i in range(len(df))]

# Create a numeric sequence for each person
df["Number"] = df.groupby("AssignedPerson").cumcount() + 1

# Sort by assigned person
df.sort_values(by="Number", inplace=True)

# Save results
df.to_csv("output.csv", index=False)