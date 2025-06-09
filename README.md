## JPyTable2 is a command-line spreadsheet program.

It uses a two-dimensional list to store the raw values in memory. This list then either gets saved directly to a file as a CSV file, or gets translated into text for display or printing to a file. It's at this translation stage where functions like math and value assignment are calculated, so the integrity of the underlying table values is maintained.

It allows the user to:

* Define a table

* Assign values to cells (duh)

* Do basic math

* Assign cells to the the values of other cells

* Assign cells to the sum of a section (or whole) of a column or row

* Save table to a CSV file or print the table display to a text file

The 2 in JPyTable2 is because I had fun writing a similar program back in high school, so I'd thought I'd give it a do-over. It's simple in concept and easy to understand at face value, but its creation requires a thousand little decisions of implementation and hidden complexity. It was fun exercise, and I know there's even more functionality I could implement, but the possible scope of a project like this could be infinite so I've cut myself off to limit any diminishing returns.