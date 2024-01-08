import guild.ipy as guild


runs = guild.runs()
print(runs.to_json())

compare = guild.runs().compare()
print(compare.to_json())