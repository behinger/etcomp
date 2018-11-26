data{
  int ntime; // timepoints
  real etdata[ntime]; // data
  vector[ntime] time; // time in s
  real tauprior; // where is the expected CP?

}
transformed data{
}
parameters {
  real<lower=0> sigma;
  real slope;
  real offset;
  real<lower=0.1, upper=time[ntime]> tau; 
  real<lower=0> autocorrfactor; 

}
transformed parameters{
 
}

model {
    // prior
    offset ~ normal(0,1);
    
    slope ~ normal(0,20);
    sigma ~ cauchy(0,5);
    tau ~ normal(tauprior,1);
    autocorrfactor ~ normal(10,20);
   { 
    vector[ntime] predict;  
    vector[ntime] w;
    w = inv_logit(autocorrfactor*(time - tau));  
  
 
    predict = offset +  w .* (slope * (time-tau)); // tau is the new offset
     
  
    etdata ~ normal(predict,sigma);
   }
  
  
  
}

generated quantities{
  
}