"""Original qualification fixtures, never a research/generalization benchmark."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    name: str
    instruction: str
    buggy: str
    oracle: str
    public: str
    hidden: str


TASKS = [
    Task("intervals", "Fix contains(start, end, value) for half-open intervals [start,end).",
         "def contains(start, end, value):\n    return start <= value <= end\n",
         "def contains(start, end, value):\n    return start <= value < end\n",
         "assert contains(1, 4, 2)\nassert not contains(1, 4, 0)\n",
         "assert not contains(1, 4, 4)\nassert not contains(2, 2, 2)\nassert contains(-3, 0, -1)\n"),
    Task("unique", "Fix unique(items): preserve first-occurrence order, support unhashable list values, do not mutate input.",
         "def unique(items):\n    return list(set(items))\n",
         "def unique(items):\n    result = []\n    for item in items:\n        if item not in result:\n            result.append(item)\n    return result\n",
         "assert unique([1, 1]) == [1]\nassert unique([]) == []\n",
         "assert unique([[2], [1], [2]]) == [[2], [1]]\nx=[3,1,3,2]\nassert unique(x)==[3,1,2]\nassert x==[3,1,3,2]\n"),
    Task("chunks", "Fix chunks(items,size): include the final partial chunk, empty input returns [], nonpositive size raises ValueError.",
         "def chunks(items, size):\n    return [items[i:i+size] for i in range(0, len(items)-size+1, size)]\n",
         "def chunks(items, size):\n    if size <= 0:\n        raise ValueError('size must be positive')\n    return [items[i:i+size] for i in range(0, len(items), size)]\n",
         "assert chunks([1,2,3,4],2)==[[1,2],[3,4]]\n",
         "assert chunks([1,2,3],2)==[[1,2],[3]]\nassert chunks([],2)==[]\ntry:\n    chunks([1],-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('negative size accepted')\n"),
    Task("merge", "Fix merge(base,override): recursively merge nested dicts; override replaces other values. Do not mutate or alias either input.",
         "def merge(base, override):\n    result = dict(base)\n    result.update(override)\n    return result\n",
         "import copy\ndef merge(base, override):\n    result=copy.deepcopy(base)\n    for key,value in override.items():\n        if isinstance(value,dict) and isinstance(result.get(key),dict):\n            result[key]=merge(result[key],value)\n        else:\n            result[key]=copy.deepcopy(value)\n    return result\n",
         "assert merge({'x':1},{'x':2})=={'x':2}\n",
         "a={'x':{'a':1,'b':2},'z':[]}\nb={'x':{'a':3},'q':[]}\nr=merge(a,b)\nassert r['x']=={'a':3,'b':2}\nr['z'].append(1)\nr['q'].append(2)\nassert a['z']==[] and b['q']==[]\nassert a['x']['a']==1\n"),
    Task("ledger", "Fix debit(balance,amount): reject negative amounts and overdrafts with ValueError; allow debit of the exact balance.",
         "def debit(balance, amount):\n    if amount >= balance:\n        raise ValueError('insufficient funds')\n    return balance - amount\n",
         "def debit(balance, amount):\n    if amount < 0 or amount > balance:\n        raise ValueError('invalid debit')\n    return balance - amount\n",
         "assert debit(10,3)==7\n",
         "assert debit(10,10)==0\nassert debit(0,0)==0\nfor amount in [-1,11]:\n    try:\n        debit(10,amount)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError('invalid amount accepted')\n"),
    Task("csv", "Fix parse_row(text): parse a single CSV record, supporting commas inside quotes, escaped quotes and empty fields. Return a list of strings.",
         "def parse_row(text):\n    return text.split(',')\n",
         "import csv\nimport io\ndef parse_row(text):\n    return next(csv.reader(io.StringIO(text)))\n",
         "assert parse_row('a,b')==['a','b']\n",
         "assert parse_row('\"a,b\",c')==['a,b','c']\nassert parse_row('a,,c')==['a','','c']\nassert parse_row('\"a\"\"b\",c')==['a\"b','c']\n"),
]
