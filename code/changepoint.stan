data {
  int ntime; // timepoints
  real etdata[ntime]; // data
  vector[ntime] time; // time in s
  real tauprior; // where is the expected CP?
}

transformed data {
}

parameters {
  real<lower=0> sigma;
  real<lower=0> slope; // enforce positivity
  real intercept; // Renamed from 'offset'
  real<lower=0, upper=time[ntime]> tau; 
}

transformed parameters {
}

model {
    // prior
    intercept ~ normal(0, 1); // Renamed from 'offset'
    
    slope ~ normal(0, 20);
    sigma ~ cauchy(0, 5);
    tau ~ normal(tauprior, 0.3);
   
    {
        vector[ntime] predict;  
        vector[ntime] w;
        w = inv_logit(150 * (time - tau));  
        predict = intercept + w .* (slope * (time - tau)); // tau is the new offset
        etdata ~ normal(predict, sigma);
    }
}

generated quantities {
}