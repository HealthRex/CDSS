from medinfo.cpoe import AssociationAnalysis

app = AssociationAnalysis.AssociationAnalysis()
app.itemsPerUpdate = 10000
app.commitUpdateBufferFromFile("finalCommitBuffer.txt")
