#!/usr/bin/python
# encoding: utf-8
import fontforge
import sys
import os

#XXX: different flags for web and desktop fonts
flags  = ("opentype", "dummy-dsig", "round", "short-post")

def generate_css(font, out, base):
    if font.fullname.lower().find("slanted")>0:
        style = "slanted"
    else:
        style = "normal"

    weight = font.os2_weight
    family = "%sWeb" %font.familyname
    name = font.fontname

    css = ""
    css += """
@font-face {
    font-style: %(style)s;
    font-weight: %(weight)s;
    font-family: "%(family)s";
    src: url('%(base)s.eot');
    src: local('☺'),
         url('%(base)s.woff') format('woff'),
         url('%(base)s.ttf') format('truetype');
}
""" %{"style":style, "weight":weight, "family":family, "base":base}

    return css

def class2pair(font, remove):
    """Looks for any kerning classes in the font and converts it to
    RTL kerning pairs."""
    kern_pairs = 0
    kern_class = 0
    new_subtable = ""
    for lookup in font.gpos_lookups:
        if font.getLookupInfo(lookup)[0] == "gpos_pair":
            for subtable in font.getLookupSubtables(lookup):
                if font.isKerningClass(subtable):
                    kern_class += 1
                    new_subtable = subtable + " pairs"
                    font.addLookupSubtable(lookup, new_subtable)
                    kclass   = font.getKerningClass(subtable)
                    klasses1 = kclass[0]
                    klasses2 = kclass[1]
                    offsets  = kclass[2]

                    for klass1 in klasses1:
                        if klass1 != None:
                            for name in klass1:
                                glyph = font.createChar(-1, name)
                                for klass2 in klasses2:
                                    if klass2 != None:
                                        kern = offsets[klasses1.index(klass1)
                                                *len(klasses2)+
                                                klasses2.index(klass2)]
                                        if kern != 0:
                                            for glyph2 in klass2:
                                                glyph.addPosSub(new_subtable,
                                                        glyph2,
                                                        kern,0,kern,0,0,0,0,0)
					        font.changed = True
                                                kern_pairs  += 1
                    if remove:
                        font.removeLookupSubtable(subtable)
    return new_subtable

def main(sfds, out):
    css = ""
    ext = os.path.splitext(out)[1].lower()
    if ext == ".css":
            css += "/* @font-face rule for Amiri */"

    for sfd in sfds:
        base = os.path.splitext(os.path.basename(sfd))[0]

        font = fontforge.open(sfd)

        if css:
            css += generate_css(font, out, base)
        else:
            class2pair(font, True)
            #XXX: should be done for web fonts only
            font.appendSFNTName ("English (US)", "License", "OFL v1.1")
            font.generate(out, flags=flags)

        font.close()

    if css:
        file = open(out, "w")
        file.write(css)
        file.close()

def usage():
    print "Usage: %s input_file output_file" % sys.argv[0]

if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1:-1], sys.argv[-1])
    else:
        usage()
        sys.exit(1)
