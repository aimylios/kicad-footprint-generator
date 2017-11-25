#!/usr/bin/env python

'''
kicad-footprint-generator is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kicad-footprint-generator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kicad-footprint-generator. If not, see http://www.gnu.org/licenses/ .
'''

import sys
import os
sys.path.append(os.path.join(sys.path[0],".."))
#sys.path.append('../..') # enable package import from parent directory

from KicadModTree import *

# parameters defined by KLC (Version 3.0.3)
klcSilkTextSize = 1.0       # silkscreen text size
klcSilkTextThickness = 0.15 # silkscreen text thickness
klcSilkLineWidth = 0.12     # silkscreen line width
klcSilkClearance = 0.2      # clearance between silkscreen and pads
klcFabTextSize = 1.0        # fabrication layer text size
klcFabTextThickness = 0.15  # fabrication layer text thickness
klcFabLineWidth = 0.1       # fabrication layer line width
klcFabBevelSize = 1.0       # maximum size of pin 1 marker on fabrication layer
klcCrtydLineWidth = 0.05    # courtyard line width
klcCrtydClearance = 0.25    # clearance between yourtyard and component or pad

# custom design parameters
fpLibrary = 'Package_SSOP'
customTextOffset = 1.2      # distance between package and name or reference
customSilkOffset = 0.05     # clearance between silk screen and package

def tvsop_gen(args):
    prefix = args['meta']['shortname']
    fpDesc = args['meta']['longname']
    fpKeys = args['meta']['keywords']
    fpDS = args['meta']['datasheet']
    pkgDimX = args['package']['size_x']
    pkgDimY = args['package']['size_y']
    pkgTolX = args['package']['tolerance_x']
    pkgTolY = args['package']['tolerance_y']
    padN = args['pad']['n']
    padDimX = args['pad']['size_x']
    padDimY = args['pad']['size_y']
    pstDimX = args['pad']['paste_x']
    pstDimY = args['pad']['paste_y']
    pitchX = args['pad']['pitch_x']
    pitchY = args['pad']['pitch_y']

    fpName = prefix + '-' + str(padN) + '_' \
             + str(pkgDimX) + 'x' + str(pkgDimY) + 'mm' + '_' \
             + 'P' + str(pitchY) + 'mm'

    # initialise KiCad footprint
    fp = Footprint(fpName)
    fp.setDescription(str(padN) + '-Lead ' + fpDesc + ' (see ' + fpDS + ')')
    fp.setTags(fpKeys)
    fp.setAttribute('smd')

    # pads on left side
    for i in range(1, int(padN/2)+1):
        # copper and solder mask layer
        tmpX = -pitchX/2
        tmpY = -(padN/2-1)*pitchY/2+(i-1)*pitchY
        fp.append(Pad(number=i,
                      type=Pad.TYPE_SMT,
                      shape=Pad.SHAPE_RECT,
                      at=[tmpX, tmpY],
                      size=[padDimX, padDimY],
                      layers=['F.Cu', 'F.Mask']))
        # paste layer
        fp.append(Pad(number='',
                      type=Pad.TYPE_SMT,
                      shape=Pad.SHAPE_RECT,
                      at=[tmpX, tmpY],
                      size=[pstDimX, pstDimY],
                      layers=['F.Paste']))

    # pads on right side
    for i in range(int(padN/2)+1, padN+1):
        # copper and solder mask layer
        tmpX = pitchX/2
        tmpY = (padN/2-1)*pitchY/2-(i-(padN/2+1))*pitchY
        fp.append(Pad(number=i,
                      type=Pad.TYPE_SMT,
                      shape=Pad.SHAPE_RECT,
                      at=[tmpX, tmpY],
                      size=[padDimX, padDimY],
                      layers=['F.Cu', 'F.Mask']))
        # paste layer
        fp.append(Pad(number='',
                      type=Pad.TYPE_SMT,
                      shape=Pad.SHAPE_RECT,
                      at=[tmpX, tmpY],
                      size=[pstDimX, pstDimY],
                      layers=['F.Paste']))

    # silkscreen
    slkDimX = pkgDimX + pkgTolX + 2*customSilkOffset + 2*(klcSilkLineWidth/2)
    slkDimY = pkgDimY + pkgTolY + 2*customSilkOffset + 2*(klcSilkLineWidth/2)
    slkMrk1X = (pitchX + padDimX)/2
    slkLimitY = ((padN/2-1)*pitchY + padDimY)/2 + klcSilkClearance
    fp.append(PolygoneLine(polygone=[[-slkDimX/2, slkLimitY],
                                     [-slkDimX/2, slkDimY/2],
                                     [slkDimX/2, slkDimY/2],
                                     [slkDimX/2, slkLimitY]],
                           width=klcSilkLineWidth,
                           layer='F.SilkS'))
    fp.append(PolygoneLine(polygone=[[-slkMrk1X, -(slkLimitY+klcSilkLineWidth/2)],
                                     [-slkDimX/2, -(slkLimitY+klcSilkLineWidth/2)],
                                     [-slkDimX/2, -slkDimY/2],
                                     [slkDimX/2, -slkDimY/2],
                                     [slkDimX/2, -slkLimitY]],
                           width=klcSilkLineWidth,
                           layer='F.SilkS'))
    fp.append(Text(type='reference',
                   text='REF**',
                   at=[0, -(pkgDimY/2+customTextOffset)],
                   size=[klcSilkTextSize, klcSilkTextSize],
                   thickness=klcSilkTextThickness,
                   layer='F.SilkS'))

    # text on fabrication layer
    fp.append(Text(type='value',
                   text=fpName,
                   at=[0, pkgDimY/2+customTextOffset],
                   size=[klcFabTextSize, klcFabTextSize],
                   thickness=klcFabTextThickness,
                   layer='F.Fab'))
    fp.append(Text(type='user',
                   text='%R',
                   at=[0, 0],
                   size=[klcFabTextSize, klcFabTextSize],
                   thickness=klcFabTextThickness,
                   layer='F.Fab'))

    # component outline on fabrication layer
    bvlDim = min(klcFabBevelSize, min(pkgDimX, pkgDimY)/4)
    fp.append(Line(start=[-pkgDimX/2+bvlDim, -pkgDimY/2],
                   end=[-pkgDimX/2, -pkgDimY/2+bvlDim],
                   width=klcFabLineWidth,
                   layer='F.Fab'))
    fp.append(Line(start=[-pkgDimX/2, -pkgDimY/2+bvlDim],
                   end=[-pkgDimX/2, pkgDimY/2],
                   width=klcFabLineWidth,
                   layer='F.Fab'))
    fp.append(Line(start=[-pkgDimX/2, pkgDimY/2],
                   end=[pkgDimX/2, pkgDimY/2],
                   width=klcFabLineWidth,
                   layer='F.Fab'))
    fp.append(Line(start=[pkgDimX/2, pkgDimY/2],
                   end=[pkgDimX/2, -pkgDimY/2],
                   width=klcFabLineWidth,
                   layer='F.Fab'))
    fp.append(Line(start=[pkgDimX/2, -pkgDimY/2],
                   end=[-pkgDimX/2+bvlDim, -pkgDimY/2],
                   width=klcFabLineWidth,
                   layer='F.Fab'))

    # courtyard
    cydDimX = pitchX + padDimX + 2*klcCrtydClearance
    cydDimY = pkgDimY + 2*klcCrtydClearance
    fp.append(RectLine(start=[-cydDimX/2, -cydDimY/2],
                       end=[cydDimX/2, cydDimY/2],
                       width=klcCrtydLineWidth,
                       layer='F.CrtYd'))

    # 3D model
    model3dName = '${KISYS3DMOD}/' + fpLibrary + '.3dshapes/' + fpName + '.wrl'
    fp.append(Model(filename=model3dName,
                    at=[0, 0, 0],
                    scale=[1, 1, 1],
                    rotate=[0, 0, 0]))

    # write file
    file_handler = KicadFileHandler(fp)
    file_handler.writeFile(fpName + '.kicad_mod')

if __name__ == '__main__':
    parser = ModArgparser(tvsop_gen)
    parser.add_parameter('name', type=str, required=True)
    parser.add_parameter('meta', type=dict, required=True)
    parser.add_parameter('package', type=dict, required=True)
    parser.add_parameter('pad', type=dict, required=True)
    parser.run()
