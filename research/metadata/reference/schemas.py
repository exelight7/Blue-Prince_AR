"""Recover Unity serialization schemas from local copied IL2CPP data."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/vendor'))
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from UnityPy.helpers.TypeTreeNode import TypeTreeNode


class Schemas:
    def __init__(self, backend='AssetsTools'):
        self.generator = TypeTreeGenerator('2021.3.45f1', generator=backend)
        self.generator.load_local_game(str(ROOT / 'backups/source'))
        self.cache = {}

    def get(self, assembly, name):
        key = (assembly, name)
        if key not in self.cache:
            # The native backend expects extensionless assembly names.
            raw = self.generator.get_nodes(assembly.removesuffix('.dll'), name)
            for item in raw:
                # The generated native header omits the serialized enabled-byte padding.
                if item.m_Level == 1 and item.m_Name == 'm_Enabled':
                    item.m_MetaFlag |= 0x4000
            nodes = [TypeTreeNode(n.m_Level, n.m_Type, n.m_Name, 0, 0,
                                 m_MetaFlag=n.m_MetaFlag) for n in raw]
            self.cache[key] = TypeTreeNode.from_list(nodes)
        return self.cache[key]
