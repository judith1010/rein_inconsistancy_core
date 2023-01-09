module ReasoningEngine = 

    #load "/mnt/tacas/ifsharp/Paket.fsx"
    Paket.Version
        [   "XPlot.Plotly", ""
            "Microsoft.Z3.x64", "~> 4.8.9"
            "AutomaticGraphLayout", "~> 1.1.9"
            "AutomaticGraphLayout.Drawing", "~> 1.1.9"
        ]
    #load "/mnt/tacas/ifsharp/Paket.Generated.Refs.fsx"
    #load "/mnt/tacas/ifsharp/XPlot.Plotly.fsx"

    #r @"/mnt/tacas/RENotebookApi/bin/Release/net472/ReasoningEngine.dll"
    #r @"/mnt/tacas/RENotebookApi/bin/Release/net472/REIN.dll"
    #r @"/mnt/tacas/RENotebookApi/bin/Release/net472/RESIN.dll"
    #r @"/mnt/tacas/RENotebookApi/bin/Release/net472/ReinMoCo.dll"
    #r @"/mnt/tacas/RENotebookApi/bin/Release/net472/RENotebookApi.dll"

    open Microsoft.Research.RENotebook

    type ReilAPI = Microsoft.Research.RENotebook.REIL
    type ReinAPI = Microsoft.Research.RENotebook.REIN
    type ResinAPI = Microsoft.Research.RENotebook.RESIN
    type MotifsAPI = Microsoft.Research.RENotebook.ReinMoCo
    module Cst = Microsoft.Research.ReasoningEngine.Constraint
    module Var = Microsoft.Research.ReasoningEngine.Var
    type TrajVis = Microsoft.Research.RENotebook.Lib.TrajectoryVisualization

    

    printfn "Loaded the Reasoning Engine (RE)."
