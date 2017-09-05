import pyparsing as pp

#Define the special variables
PLUS, DASH = map(pp.Suppress, "+-")
COLON, LBRACK, RBRACK, LBRACE, RBRACE, TILDE, CARAT, COMMA = map(pp.Suppress, ":[]{}~^,")
UNDERSCORE, DOT, BSLASH, SLASH = map(pp.Literal, '_./\\')
LPAR, RPAR = map(pp.Suppress, "()")
SEMICOLON, DQUOTA = map(pp.Suppress, ';"')
SQUOTA = map(pp.Suppress, "'")
STAR = map(pp.Literal, '*')

dashLine = pp.Suppress(pp.Group(pp.OneOrMore('-')))
starLine = pp.Suppress(pp.Group(pp.OneOrMore('*')))
date     = pp.Word(pp.alphanums + " " + ":")

##quota define
squotes = pp.QuotedString("'")
dquotes = pp.QuotedString('"')
stars   = pp.QuotedString('*')
eques   = pp.QuotedString('=')
tildes  = pp.QuotedString('~')
angles  = pp.QuotedString('<', endQuoteChar='>')
braces  = pp.QuotedString('{', endQuoteChar='}')
bracks  = pp.QuotedString('[', endQuoteChar=']')
paras   = pp.QuotedString('(', endQuoteChar=')')


#Define the name rule
floatNum    = pp.Word(pp.nums + '.' + "_" + "-")
floatZero   = pp.Word("0" + '.')
intNum      = pp.Word(pp.nums + '-')
flatName    = pp.Word(pp.alphanums + "_")
hierName    = pp.Word(pp.alphanums + '/' + '_' + '[' + ']')
libCellName = pp.Word(pp.alphas.upper() + pp.nums + "_")

#Timing related
toggleType  = pp.Word("r" + "f" + "rise" + "fall")
pathType    = pp.Word("min" + "max" + "Min" + "Max")
pathCol     = pp.Word("Fanout" + "Cap" + "Trans" + "Incr" + "Path")
clkType     = pp.Word("ideal" + "propagated")
annoType    = pp.Word("&" + "*")
pathGroup   = pp.Word(pp.alphanums + '\*' + '_' + "'")
scenarioName= pp.Word(pp.alphanums + "_" + "'")

#DEF varible
orient       = pp.oneOf("N E  W  S  FN  FE  FW  FS")
routeDir     = pp.oneOf("X Y")
placeStatus  = pp.oneOf("PLACED FIXED COVER UNPLACED")
oxide        = pp.oneOf("OXIDE1 OXIDE2 OXIDE3 OXIDE4")
pinDir       = pp.oneOf("INPUT OUTPUT INOUT")
pinUse       = pp.oneOf("SIGNAL POWER GROUND CLOCK TIEOFF ANALOG SCAN RESET")
propObjType  = pp.oneOf("COMPONENT COMPONENTPIN DESIGN GROUP NET NONDEFAULTRULE REGION ROW SPECIALNET")
propType     = pp.oneOf("INTERGER REAL STRING")
objectType   = pp.oneOf("DESIGN COMPONENT NET SPECIALNET GROUP ROW COMPONENT REGION")
#pinAttrName  = pp.oneOf("NET SPECIAL DIRECTION  NETEXPR SUPPLYSENSITIVITY GROUNDSENSITIVITY USE ANTENNAPINMAXAREACAR ANTENNAPINMAXCUTCAR ANTENNAPINDIFFAREA ANTENNAMODEL ANTENNAPINGATEAREA ANTENNAPINPARTIALMETALAREA ANTENNAPINPARTIALMETALAREA ANTENNAPINPARTIALCUTAREA")
pinAttrName  = pp.oneOf("NET  DIRECTION  USE")
routeBkgAttr = pp.oneOf("SLOTS FILLS PUSHDOWN EXCEPTPGNET COMPONENT SPACING DESIGNRULEWIDTH MASK")
cellBkgAttr  = pp.oneOf("SOFT PARTIAL COMPONENT PUSHDOWN ")
bkgAttr = pp.oneOf("SLOTS FILLS PUSHDOWN EXCEPTPGNET COMPONENT SPACING DESIGNRULEWIDTH MASK SOFT PARTIAL COMPONENT PUSHDOWN ")
extAttr      = pp.oneOf("CREATOR DATE REVISION")
shapeType    = pp.oneOf("RECT POLYGON")
netAttr      = pp.oneOf("SHIELDNET XTALK NONDEFAULTRULE SOURCE FIXEDBUMP FREQUENCY ORIGINAL USE PATTERN ESTCAP WEIGHT")
netSource    = pp.oneOf("NETLIST DIST USER TIMING")
netPattern   = pp.oneOf("BALANCED STEINER TRUNK WIREDLOGIC")
wireState    = pp.oneOf("COVER FIXED ROUTED NOSHIELD")


proptyDef    = pp.Group(PLUS + "PROPERTY" + pp.OneOrMore(pp.delimitedList(braces)))
# polygon
origX        = pp.Word(pp.nums + "*" + "-")
origY        = pp.Word(pp.nums + "*" + "-")
orig         = pp.Group(pp.Optional(LPAR) + origX + origY + pp.Optional(RPAR))
rectangle    = pp.Group(orig + orig)
polygon      = pp.Group(orig + pp.OneOrMore(orig))

# Process Varible
layerName    = pp.oneOf("M0 M1 M2 M3 M4 M5 M6 M7 M8 M9 M10 M11 M12 M13 AP VIA0 VIA1 VIA2 VIA3 VIA4 VIA5 VIA6 VIA7 VIA8 VIA9 VIA10 VIA11 VIA12 RV")
metalName    = pp.oneOf("M0 M1 M2 M3 M4 M5 M6 M7 M8 M9 M10 M11 M12 M13 AP")
cutName      = pp.oneOf("VIA0 VIA1 VIA2 VIA3 VIA4 VIA5 VIA6 VIA7 VIA8 VIA9 VIA10 VIA11 VIA12 RV")

#DEF Pattern
'''
Blockages  1
Bus Bit Characters
Components
Design
Die Area
Divider Character
Extensions
Fills
GCell Grid
Groups
History
Nets
Regular Wiring Statement
Nondefault Rules
Pins
Pin Properties
Property Definitions
Regions
Rows
Scan Chains
Slots
Special Nets
Special Wiring Statement
Styles
Technology
Tracks
Units
Version
Vias
'''
#Commnon layer
metaLayer    = pp.Group("LAYER" + metalName)
location     = pp.Group(placeStatus + orig + orient)
namePair     = pp.Group(pp.Optional(LPAR) + hierName + hierName + pp.Optional(RPAR))
maskLayer    = pp.Group("MASK" + intNum)
shape        = pp.Group(shapeType + polygon)
compMaskShift = pp.Group("COMPONENTMASKSHIFT " + pp.OneOrMore(layerName))
maskShift = pp.Group("MASKSHIFT" + intNum)

# Blockages
layerBkg = pp.Group(DASH + "LAYER" + layerName + PLUS +
                    pp.Optional(routeBkgAttr + pp.Optional(hierName) + PLUS )  +
                    pp.oneOf("RECT POLYGON") + polygon +
                    SEMICOLON
                    )
bkgType = pp.Group(DASH + pp.oneOf("PLACEMENT LAYER") + PLUS +
                    pp.oneOf("RECT POLYGON") + polygon +
                    SEMICOLON
                   )

cellBkg = pp.Group(DASH + pp.oneOf("PLACEMENT LAYER") + pp.Optional(layerName) + PLUS +
                   pp.Optional(bkgAttr+ pp.Optional(hierName)) +
                   pp.OneOrMore(pp.oneOf("RECT POLYGON") + polygon) +
                   SEMICOLON
                   )
#bkgSect = pp.Group("BLOCKAGES" + intNum +
#                   pp.ZeroOrMore(layerBkg) +
#                   pp.ZeroOrMore(cellBkg)
#                   )
# Bus Bit Characters
busbitchars     =  pp.Group("BUSBITCHARS" + pp.delimitedList(dquotes) + SEMICOLON)
# COMPONENTMASKSHIFT
compMaskShift   =  pp.Group("COMPONENTMASKSHIFT " + pp.OneOrMore(layerName))

# COMPONENTS
cellLoc = pp.Group(PLUS + placeStatus + pp.Optional(orig) + pp.Optional(orient))
compDefine = pp.Group(DASH + hierName + hierName +
                      pp.Optional(PLUS + "EEQMASTER" + hierName) +
                      pp.Optional(PLUS + "SOURCE" + pp.oneOf("NETLIST DIST USER TIMING")) +
                      pp.Optional(cellLoc) +
                      pp.Optional(PLUS + maskShift) +
                      pp.Optional(PLUS + "HALO" + pp.Optional("SOFT") + rectangle) +
                      pp.Optional(PLUS + "ROUTEHALO" + intNum + layerName + layerName) +
                      pp.Optional(PLUS + "WEIGHT" + intNum) +
                      pp.Optional(PLUS + "REGION" + hierName) +
                      pp.Optional(proptyDef) +
                      SEMICOLON
                      )
compSect = pp.Group("COMPONENTS" + intNum + SEMICOLON + pp.OneOrMore(compDefine) + "END COMPONENTS")
# DESIGN
designName      =  pp.Group("DESIGN" + hierName + SEMICOLON)

#Die Area
die_area        =  pp.Group("DIEAREA" + polygon + SEMICOLON)

#Divider Character
dividerchar     =  pp.Group("DIVIDERCHAR" + pp.delimitedList(dquotes) + SEMICOLON)

#Extensions
extensionText   = pp.Group("BEGINEXT " + pp.delimitedList(squotes) +
                            extAttr + pp.delimitedList(squotes) +
                           "ENDEXT"
                           )
#FIills
fillLayer   = pp.Group(DASH + "LAYER" + metalName + pp.Optional(PLUS + "MASK" + intNum) + pp.Optional(PLUS + "OPC") +
                       pp.OneOrMore(shapeType + polygon) + SEMICOLON
                       )
fillVia     = pp.Group(DASH + "VIA" + cutName + pp.Optional(PLUS + "MASK" + intNum) + pp.Optional(PLUS + "OPC") +
                       pp.OneOrMore(orig) + SEMICOLON
                       )
fillSect    = pp.Group("FILLS" + intNum + SEMICOLON +
                        pp.ZeroOrMore(fillLayer) +
                        pp.ZeroOrMore(fillVia) +
                       "END FILLS"
                       )

#GCell Grid
gcellGridSect  = pp.Group( pp.ZeroOrMore("GCELLGRID" +
                                         pp.OneOrMore(routeDir + intNum + "DO" + intNum + "STEP" + intNum) +
                                         SEMICOLON)
                          )
# Groups
groupDef   = pp.Group(DASH + hierName + hierName +
                      pp.Optional(PLUS + "REGION" + hierName) +
                      pp.ZeroOrMore(proptyDef) + SEMICOLON
                      )
groupSect  = pp.Group("GROUPS" + intNum +
                      pp.OneOrMore(groupDef) +
                      "END GROUPS"
                      )

#History
history         =  pp.Group("HISTORY" + hierName + SEMICOLON)

#NETS
#NETS is partical supported
taper        = pp.Group("TAPER")
routePoint   = pp.Group( pp.OneOrMore(pp.OneOrMore(orig) + pp.Optional(maskLayer)) + hierName)
routeWire    = pp.Group(PLUS + wireState +
                        layerName + pp.Optional("TAPER") +
                        routePoint +
                        pp.ZeroOrMore("NEW" + layerName + pp.Optional("TAPER") +
                                        routePoint
                                    )
                        )
netVpin      = pp.Group(PLUS + "VPIN" + hierName + pp.Optional(metaLayer) + orig + location)
netSubnet    = pp.Group(PLUS + "SUBNET" + hierName + pp.ZeroOrMore(namePair) + routeWire)
netDefine    = pp.Group(DASH + flatName + pp.OneOrMore(namePair) +
                        pp.ZeroOrMore(netVpin) +
                        pp.ZeroOrMore(netSubnet) +
                        pp.ZeroOrMore(namePair) +
                        pp.Optional(proptyDef) + SEMICOLON
                        )
netSect      = pp.Group("NETS" + intNum +
                        pp.OneOrMore(netDefine) +
                        "END NETS"
                        )
# NonDefault rule
ndrLayer = pp.Group(PLUS + "LAYER" + layerName + "WIDTH" + intNum +
                    pp.Optional("DIAGWIDTH" + intNum) +
                    pp.Optional("SPACING" + intNum) +
                    pp.Optional("WIREEXT" + hierName))

ndrDefine = pp.Group(DASH + hierName +
                     pp.Optional(PLUS + "HARDSPACING") +
                     pp.OneOrMore(ndrLayer) +
                     pp.Optional(PLUS + "VIA" + hierName) +
                     pp.Optional(PLUS + "VIARULE" + hierName) +
                     pp.ZeroOrMore(PLUS + "MINCUTS" + cutName + intNum) +
                     pp.ZeroOrMore(proptyDef) +
                     SEMICOLON)
ndrSect = pp.Group("NONDEFAULTRULES" + intNum + SEMICOLON + pp.OneOrMore(ndrDefine) + "END NONDEFAULTRULES")


#PIN SECTION
shapeAttr = pp.oneOf("MASK SPACING DESIGNRULEWIDTH")
'''
portShape = pp.Group(PLUS + pp.oneOf("POLYGON LAYER VIA") + layerName +
                             pp.ZeroOrMore(shapeAttr + intNum) +
                             polygon)
'''
#portShape  = pp.Group(PLUS + "LAYER" + layerName + rectangle)
portShape  = pp.Group("LAYER" + layerName + rectangle)
portStatus = pp.Group( placeStatus + orig + orient)

#portDefine = pp.Group(pp.Optional(PLUS + "PORT") +
#                      pp.Optional(portShape) +
#                      pp.Optional(portStatus)
#                      )


portDefine = pp.Group(pp.Optional(portShape) +
                      pp.Optional(portStatus)
                      )

#portAttr = pp.Group(PLUS + pinAttrName + pp.Optional(hierName))
portAttr = pp.Group(PLUS + flatName + hierName)

'''

pinDefine = pp.Group(DASH + hierName +
                     pp.OneOrMore(portAttr) +
                      )
'''
pinDefine = pp.Group(DASH + hierName +
                     pp.OneOrMore( portAttr) +
                     portShape +
                     portStatus +
                     SEMICOLON
                     )
#PINPROPERTIES
pinProperty     = pp.Group( DASH + namePair + pp.ZeroOrMore(proptyDef) + SEMICOLON)
pinPropSect     = pp.Group("PINPROPERTIES" + intNum +
                           pp.OneOrMore(pinProperty) +
                           "END PINPROPERTIES"
                           )
#Property Definitions
propDef      = pp.Group(pp.OneOrMore(flatName + propType + pp.Optional("RANGE"+ namePair) +  flatName + SEMICOLON))
propSect     = pp.Group("PROPERTYDEFINITIONS" +
                        pp.OneOrMore(propDef) +
                        "END PROPERTYDEFINITIONS"
                        )
# REGION SECTION
regionDefine = pp.Group(DASH + hierName + polygon +
                        pp.Optional(PLUS + "TYPE" + pp.oneOf("FENCE GUIDE")) +
                        pp.ZeroOrMore(proptyDef) +
                        SEMICOLON)
regionSect = pp.Group("REGIONS" + intNum + SEMICOLON + pp.OneOrMore(regionDefine) + "END REGIONS")

#ROW
row = pp.Group("ROW" + hierName + hierName + orig + orient +
               pp.Optional(
                   "DO" + intNum + "BY" + intNum + pp.Optional("STEP" + intNum + intNum)) +
               pp.Optional(PLUS + "PROPERTY" + pp.OneOrMore(pp.delimitedList(braces))) + SEMICOLON)
rows = pp.Group(pp.OneOrMore(row))

#Scan Chains
# not support
chainDefine = pp.Group(DASH + hierName +
                       pp.Optional(PLUS + "PARTITION " + hierName + pp.Optional("MAXBITS" + intNum)) +
                       pp.Optional(PLUS + "COMMONSCANPINS" + pp.ZeroOrMore( pp.delimitedList(paras)) )
                      )

# Slot
slotSect    = pp.Group("SLOTS" + intNum +
                       pp.ZeroOrMore(DASH + metaLayer + pp.OneOrMore(shape) + SEMICOLON) +
                       "END SLOTS"
                       )
# Special Nets
#not support

#Technology
technology      =  pp.Group("TECHNOLOGY" + hierName + SEMICOLON)
#Track
track = pp.Group("TRACKS" + routeDir + intNum + "DO" + intNum + "STEP" + intNum +
                 pp.Optional("MASK" + intNum + pp.Optional("SAMEMASK")) +
                 pp.Optional("LAYER" + layerName) + ';')
tracks = pp.Group(pp.OneOrMore(track))

#Unit
unit            =  pp.Group("UNITS DISTANCE MICRONS" + intNum + SEMICOLON)
#Version
version         =  pp.Group("VERSION" + floatNum + SEMICOLON)
# VIA SECTION
viaRule = pp.Group(PLUS + "VIARULE" + hierName +
                   PLUS + "CUTSIZE" + intNum + intNum +
                   PLUS + "LAYERS" + metalName + cutName + metalName +
                   PLUS + "CUTSPACING" + intNum + intNum +
                   PLUS + "ENCLOSE" + intNum + intNum + intNum + intNum +
                   pp.Optional(PLUS + "ROWCOL" + intNum + intNum) +
                   pp.Optional(PLUS + "ORIGIN" + intNum + intNum) +
                   pp.Optional(PLUS + "OFFSET" + intNum + intNum + intNum + intNum) +
                   pp.Optional(PLUS + "PATTERN" + hierName)
                   )
viaRect = pp.Group(
    PLUS + "RECT" + layerName + pp.Optional(PLUS + "MASK" + intNum) + rectangle)
viaPoly = pp.Group(
    PLUS + "polygon" + layerName + pp.Optional(PLUS + "MASK" + intNum) + polygon)
viaDefine = pp.Group(DASH + hierName + pp.Optional(viaRule) + pp.ZeroOrMore(viaRect) + pp.ZeroOrMore(
    viaPoly) + SEMICOLON)
viaSect = pp.Group("VIAS" + intNum + SEMICOLON + pp.OneOrMore(viaDefine) + "END VIAS")


# Property Define

