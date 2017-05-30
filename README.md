# def2json
convert the DEF file to json format
Json hash define.

ROW => {$rowName}
        => {rowSite}
        =>

TRACK => [TRACK Y ]
         [TRACY X ]

VIAS => {$viaName} =>
        => {RECT} => [ $shape1 $shape2 ]

NDR => {$ruleName}  = [$ndr ]

COMP => {$instName} =>
            [$status $orig $orient]

PIN => {$pinName} =>
        => {NET}
        => {DIRECTION}
        => {USE}
        => {LAYER}  =  [$shape1 $shape2 ]
        => {STATE} =  [$status $orig $orient ]
BKG => {$bkgName} =>
        => ["layer spacing polygon"]



##Net Section is hard to support
NET => {$netName} =>
SPECIALNET


