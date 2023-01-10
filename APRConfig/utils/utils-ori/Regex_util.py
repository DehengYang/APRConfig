"""
some examples:

pattern = re.compile(
    r'\[PV_INFO\] curStmt: SourceLocation .* singleCompileTimeCost: (.*), singlePVTimeCost: (.*) pvInfo: (.*) NTCE: (.*)'
)
match = re.findall(pattern, line)[0]
cnt = 0
singleCompileTimeCost = float(match[cnt])
cnt += 1
singlePVTimeCost = float(match[cnt])
cnt += 1
pvInfo = match[cnt]
cnt += 1
NTCE = int(match[cnt])

"""
import re


def findall(compile_string, dst_string):
    pattern = re.compile(compile_string)
    matches = re.findall(pattern, dst_string)
    return matches