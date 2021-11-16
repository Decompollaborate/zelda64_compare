#!/usr/bin/python3

from __future__ import annotations

from mips.GlobalConfig import GlobalConfig

from .Utils import *
import ast

class ContextFile:
    def __init__(self, name: str, vram: int):
        self.name: str = name
        self.vram: int = vram
        #self.references: List[int] = list()

class ContextSegment:
    def __init__(self, segmentName: str, segmentInputPath: str, segmentType: str, subsections):
        self.name: str = segmentName
        self.inputPath: str = segmentInputPath
        self.type: str = segmentType
        self.subsections: list = subsections

class ContextVariable:
    def __init__(self, vram: int, name: str):
        self.vram: int = vram
        self.name: str = name
        self.type: str = ""
        self.arrayInfo: str = ""
        self.size: int = 4

class Context:
    def __init__(self):
        self.files: Dict[int, ContextFile] = dict()
        self.segments: Dict[str, ContextSegment] = dict()

        self.funcsInFiles: Dict[str, List[int]] = dict()
        self.symbolToFile: Dict[int, str] = dict()

        self.funcAddresses: Dict[int, str] = dict()

        self.labels: Dict[int, str] = dict()
        self.symbols: Dict[int, ContextVariable] = dict()

        # Where the jump table is
        self.jumpTables: Dict[int, str] = dict()
        # The addresses each jump table has
        self.jumpTablesLabels: Dict[int, str] = dict()

        # Functions jumped into Using J instead of JAL
        self.fakeFunctions: Dict[int, str] = dict()


    def getAnySymbol(self, vramAddress: int) -> str|None:
        if vramAddress in self.funcAddresses:
            return self.funcAddresses[vramAddress]

        if vramAddress in self.jumpTablesLabels:
            return self.jumpTablesLabels[vramAddress]

        if vramAddress in self.labels:
            return self.labels[vramAddress]

        if vramAddress in self.jumpTables:
            return self.jumpTables[vramAddress]

        if vramAddress in self.symbols:
            return self.symbols[vramAddress].name

        if vramAddress in self.fakeFunctions:
            return self.fakeFunctions[vramAddress]

        return None

    def getGenericSymbol(self, vramAddress: int, tryPlusOffset: bool = True) -> str|None:
        if vramAddress in self.funcAddresses:
            return self.funcAddresses[vramAddress]

        if vramAddress in self.jumpTables:
            return self.jumpTables[vramAddress]

        if vramAddress in self.symbols:
            return self.symbols[vramAddress].name

        if GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET and tryPlusOffset:
            # merges the dictionaries
            vramSymbols = sorted({**self.funcAddresses, **self.jumpTables, **self.symbols}.items(), reverse=True)
            for vram, symbol in vramSymbols:
                symbolSize = 4
                if isinstance(symbol, ContextVariable):
                    symbolSize = symbol.size
                if vramAddress > vram and vramAddress < vram + symbolSize:
                    symbolName = symbol
                    if isinstance(symbol, ContextVariable):
                        symbolName = symbol.name
                    return f"{symbolName} + {toHex(vramAddress - vram, 1)}"

        return None

    def getSymbol(self, vramAddress: int, tryPlusOffset: bool = True, checkUpperLimit: bool = True) -> ContextVariable|None:
        if vramAddress in self.symbols:
            return self.symbols[vramAddress]

        if GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET and tryPlusOffset:
            vramSymbols = sorted(self.symbols.items(), reverse=True)
            for vram, symbol in vramSymbols:
                symbolSize = symbol.size
                if vramAddress > vram:
                    if checkUpperLimit:
                        if vramAddress >= vram + symbolSize:
                            continue
                    return symbol
        return None

    def getGenericLabel(self, vramAddress: int) -> str|None:
        if vramAddress in self.jumpTablesLabels:
            return self.jumpTablesLabels[vramAddress]

        if vramAddress in self.labels:
            return self.labels[vramAddress]

        return None

    def getFunctionName(self, vramAddress: int) -> str|None:
        if vramAddress in self.funcAddresses:
            return self.funcAddresses[vramAddress]

        return None


    def addFunction(self, filename: str|None, vramAddress: int, name: str):
        #if filename is not None and filename in self.files:
        #    if vramAddress not in self.files[filename].references:
        #        self.files[filename].references.append(vramAddress)
        if vramAddress not in self.funcAddresses:
            self.funcAddresses[vramAddress] = name
        if vramAddress not in self.symbolToFile and filename is not None:
            self.symbolToFile[vramAddress] = filename


    def readFunctionMap(self, version: str):
        functionmap_filename = f"functionmap/{version}.csv"
        if not os.path.exists(functionmap_filename):
            return

        functionmap_file = readCsv(functionmap_filename)
        for row in functionmap_file:
            filename = row[0]
            vram = int(row[1], 16)
            func_name = row[2]

            if filename not in self.funcsInFiles:
                self.funcsInFiles[filename] = []
            self.funcsInFiles[filename].append(vram)
            self.funcAddresses[vram] = func_name
            self.symbolToFile[vram] = filename

    def readMMAddressMaps(self, filesPath: str, functionsPath: str, variablesPath: str):
        with open(filesPath) as infile:
            files_spec = ast.literal_eval(infile.read())

        for segmentName, segmentInputPath, segmentType, subsections, subfiles  in files_spec:
            self.segments[segmentName] = ContextSegment(segmentName, segmentInputPath, segmentType, subsections)
            for vram, subname in subfiles.items():
                if subname == "":
                    subname = f"{segmentName}_{toHex(vram, 8)[2:]}"
                self.files[vram] = ContextFile(subname, vram)

        with open(functionsPath) as infile:
            functions_ast = ast.literal_eval(infile.read())

        for vram, funcData in functions_ast.items():
            funcName = funcData[0]
            self.addFunction(None, vram, funcName)

        with open(variablesPath) as infile:
            variables_ast = ast.literal_eval(infile.read())

        for vram, varData in variables_ast.items():
            varName, varType, varArrayInfo, varSize = varData
            contVar = ContextVariable(vram, varName)
            contVar.type = varType
            contVar.arrayInfo = varArrayInfo
            contVar.size = varSize
            self.symbols[vram] = contVar

    def readVariablesCsv(self, filepath: str):
        if not os.path.exists(filepath):
            return

        variables_file = readCsv(filepath)
        for row in variables_file:
            if len(row) == 0:
                continue

            vram, varName, varType, varSize = row

            vram = int(vram, 16)
            varSize = int(varSize, 0)
            contVar = ContextVariable(vram, varName)
            contVar.type = varType
            contVar.size = varSize
            self.symbols[vram] = contVar

    def readFunctionsCsv(self, filepath: str):
        if not os.path.exists(filepath):
            return

        functions_file = readCsv(filepath)
        for row in functions_file:
            if len(row) == 0:
                continue

            vram, funcName = row

            vram = int(vram, 16)
            self.addFunction(None, vram, funcName)

    def saveContextToFile(self, filepath: str):
        with open(filepath, "w") as f:
            for address, name in self.funcAddresses.items():
                file = self.symbolToFile.get(address, "")
                jal = (address & 0x00FFFFFF) >> 2
                jal = 0x0C000000 | jal
                f.write(f"function,{file},{toHex(address, 8)},{name},{toHex(jal, 8)}\n")

            for address, name in self.jumpTables.items():
                file = self.symbolToFile.get(address, "")
                f.write(f"jump_table,{file},{toHex(address, 8)},{name},\n")

            for address, name in self.jumpTablesLabels.items():
                file = self.symbolToFile.get(address, "")
                f.write(f"jump_table_label,{file},{toHex(address, 8)},{name},\n")

            for address, name in self.labels.items():
                file = self.symbolToFile.get(address, "")
                f.write(f"label,{file},{toHex(address, 8)},{name},\n")

            for address, symbol in self.symbols.items():
                file = self.symbolToFile.get(address, "")
                f.write(f"symbol,{file},{toHex(address, 8)},{symbol.name},{symbol.type},{symbol.size}\n")

            for address, name in self.fakeFunctions.items():
                file = self.symbolToFile.get(address, "")
                f.write(f"fake_function,{file},{toHex(address, 8)},{name},\n")

