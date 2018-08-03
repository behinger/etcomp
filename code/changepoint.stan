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
  real<lower=0> slope; // enforce positivity
  real offset;
  real<lower=0, upper=time[ntime]> tau; 


}
transformed parameters{
 
}

model {
    // prior
    offset ~ normal(0,1);
    
    slope ~ normal(0,20);
    sigma ~ cauchy(0,5);
    tau ~ normal(tauprior,0.3);
   
   { 
    vector[ntime] predict;  
    vector[ntime] w;
    w = inv_logit(150*(time - tau));  
  
 
    predict = offset +  w .* (slope * (time-tau)); // tau is the new offset
     
  
    etdata ~ normal(predict,sigma);
   }
  
  
  
}

generated quantities{
  
}