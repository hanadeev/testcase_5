#!/srv/anaconda3/bin/python3.7

import os
import sys


class Engine:
    @classmethod
    def scan(cls, files: tuple = ('file1', 'file2')) -> str:
        result_list = []
        for file_ in files:
            result = cls._check_file(file_)
            result_list.append(cls._format_result(file_, result))
        return '\n'.join(result_list)
        # return cls._format_result('test.txt', 'failed')

    @staticmethod
    def _format_result(file_: str, result: str) -> str:
        return "{}: {}".format(file_, result)

    @staticmethod
    def _check_file(file_: str) -> str:
        return '<Result>'


class EngineA(Engine):
    @staticmethod
    def _format_result(file_: str, result: str):
        return "{} scanned. Result: {}".format(file_, result)


class EngineB(Engine):
    @staticmethod
    def _format_result(file_: str, result: str):
        return "{{'{}': '{}'}}".format(file_, result)


class EngineC(Engine):
    @staticmethod
    def _format_result(file_: str, result: str):
        return "{}|||{}".format(file_, result)


class EngineD(Engine):
    @staticmethod
    def _format_result(file_: str, result: str):
        return "{} from {}".format(result, file_)


class EngineE(Engine):
    @staticmethod
    def _format_result(file_: str, result: str):
        return "The {} is {}".format(file_, result)


if __name__ == '__main__':
    print(sys.argv)
    print(Engine.scan())
    print(EngineA.scan())
    print(EngineB.scan())
    print(EngineC.scan())
    print(EngineD.scan())
    print(EngineE.scan())
    # s.start()
