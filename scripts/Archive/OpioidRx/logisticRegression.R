df = read.csv("processed.tab",sep="\t");

driver = function(df)
{
  formula = hasDrugScreens ~ postIntervention + age + Male + White + Black.or.African.American + nOpioidRx
  model = glm(formula, data=df, family=binomial);
  return(model);
}