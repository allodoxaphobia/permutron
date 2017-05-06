# permutron.py

Generates passwords likely to be made by a human based of keywords.
Use it to built a custom bruteforce wordlist if you believe passwords are human generated.

Usage:
Enter words likely to be included in password to words.txt. One word per line
If you are uncertain what to add, here's a good starter:
admin
nameofproduct
nameofvendor
nameofclient
nameofserver

in permutron.conf, update the value of the human_pass setting to your desire, excepts values 0-5 where:
0 - is all permutations will be generated and more, less likely characters are used in permutation
5 - more rigerous checks on likelyhood and more limited character sets are used to generate permutations

Generally I would advice to set it to 3-5 if you are generating a wordlist for networked devices. If you are using the wordlist for offline bruteforcing, use 0

permutron.conf also contains a password policies section. If you know the password policies used when the password was set then update this section accordingly, set use_policy to 0 to skip policy validation checks.
