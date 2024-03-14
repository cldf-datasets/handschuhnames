import pathlib
import collections

from clldutils.misc import slug
from cldfbench import Dataset as BaseDataset, CLDFSpec

from pybtex.database import parse_string


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "handschuhnames"

    def cldf_specs(self):  # A dataset must declare all CLDF sets it creates.
        return CLDFSpec(
            module='StructureDataset',
            dir=self.cldf_dir,
            metadata_fname='cldf-metadata.json')

    def cmd_download(self, args):
        self.raw_dir.xlsx2csv('Handschuh_Names.xlsx')

    def cmd_makecldf(self, args):
        args.writer.cldf.add_component('LanguageTable')
        args.writer.cldf.add_component('CodeTable')
        args.writer.cldf.add_component('ParameterTable', 'Section')

        params = collections.OrderedDict()
        for row in self.etc_dir.read_csv('parameters.csv', dicts=True):
            params[row['ID']] = []
            args.writer.objects['ParameterTable'].append(dict(
                ID=slug(row['ID']),
                Name=row['Name'],
                Section=row['Section'],
            ))

        liso2gl = {l.iso: l for l in args.glottolog.api.languoids() if l.iso}
        for i, row in enumerate(self.raw_dir.read_csv('Handschuh_Names.Tabelle1.csv', dicts=True)):
            iso, glottocode = row['ISO'], None
            if row['ISO'] == "nni/nxl":
                iso, glottocode = None, "nuau1240"
            glang = liso2gl[iso] if iso else args.glottolog.api.languoid(glottocode)

            if (source_str := row.get('Source')):
                src = [source_str]
            else:
                src = []

            args.writer.objects['LanguageTable'].append(dict(
                ID=slug(row['ISO']),
                Name=row['Language'],
                Glottocode=glang.id,
                ISO639P3code=iso,
                Latitude=glang.latitude,
                Longitude=glang.longitude,
            ))
            for k in params:
                if row[k] not in params[k]:
                    params[k].append(row[k])
                    args.writer.objects['CodeTable'].append(dict(
                        ID='{}-{}'.format(slug(k), slug(row[k])),
                        Name=row[k],
                        Parameter_ID=slug(k),
                    ))
                args.writer.objects['ValueTable'].append(dict(
                    ID='{}-{}'.format(iso, slug(k)),
                    Code_ID='{}-{}'.format(slug(k), slug(row[k])),
                    Value=row[k],
                    Language_ID=slug(row['ISO']),
                    Parameter_ID=slug(k),
                    Source=src,
                ))
        args.writer.objects['CodeTable'] = sorted(args.writer.objects['CodeTable'], key=lambda i: i['ID'])

        sources = parse_string(self.raw_dir.read('Handschuh-Names.bib'), 'bibtex')
        args.writer.cldf.add_sources(sources)
