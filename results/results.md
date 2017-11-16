# Online Learning Results

## Online Options:

### scaler

* _none_: do not update scaler at online stage
* _one_: maintain one scaler per feature, update it at online stage
* _multi_: create and update scalers for each feature on-the-fly (up to 10)

### clf

* _none_: do not update classifier at online stage
* _regular_: fit classifier incrementally for each sample obtained at online stage
* _window_: fit classifier with a window of online samples whenever false negtive is detected

## Result Set # 1
**Training sets**: HTTP_10KB with 300 data points   
**Testing sets**: HTTP_30KB, HTTP_50KB, HTTP_70KB, HTTP_90KB  
**Labelling**: 1 if _vnf.decoder.pkts > 0.7 * cap_, else 0   

Note that window-based training detects false negtive by matching input and output and labels data points with _0.7 * vnf.decoder.bytes_.

**Conclusion**   
For this testing set:
1. Training classifier online is more important than updating scalers online.
2. **Window-based** learning performs worse than **regular** learning. First, window-based learning performs less number of retrainings (only at false negtive). Second, window-based training is not based on "ground truth" targets as regular learning does.
3. **multi** scaler works slightly worse than **one** scaler. This is not exactly we expect. I am digging into it to figure out why. Possibly this is because the values of different distributions of the same feature overlap, which makes it very hard to create accurate scalers to separate them. For instance, [**this**](https://github.com/lianjiecao/envi/blob/master/results/scaler_multi-clf_regular-http.md) shows scalers for _vnf.app_layer.flow.http_ does not increase linearly as more testing sets are added. When the first testing set is added, it does create a new scaler and keeps updating the new scaler. However, when more testing sets are added, no new scalers are created. It simply keeps updating the second scaler. Also, some features has unexpected large number of scalers.

**Examples of scalers not growing as expected**
```bash
### Testing HTTP_30KB [finished HTTP_10KB]
+++++ vnf.app_layer.flow.http +++++
2 scalers:
  280 samples, mean 639.8198, var 29659.2863
  317 samples, mean 238.7158, var 3887.3889
### Testing HTTP_50KB [finished HTTP_10KB,HTTP_30KB]
+++++ vnf.app_layer.flow.http +++++
2 scalers:
  280 samples, mean 639.8198, var 29659.2863
  317 samples, mean 238.7158, var 3887.3889
### Testing HTTP_70KB [finished HTTP_10KB,HTTP_30KB,HTTP_50KB]
+++++ vnf.app_layer.flow.http +++++
2 scalers:
  280 samples, mean 639.8198, var 29659.2863
  957 samples, mean 159.3589, var 5476.1230
### Testing HTTP_90KB [finished HTTP_10KB,HTTP_30KB,HTTP_50KB,HTTP_70KB]
+++++ vnf.app_layer.flow.http +++++
2 scalers:
  280 samples, mean 639.8198, var 29659.2863
  957 samples, mean 159.3589, var 5476.1230
```

```bash
### Trained on HTTP_10KB,HTTP_30KB,HTTP_50KB,HTTP_70KB,HTTP_90KB
+++++ vnf.http.memuse +++++
10 scalers:
  1007 samples, mean -8604.7455, var 1479978673.1291
  137 samples, mean 140202.8446, var 2268924327.4395
  46 samples, mean 1071401.1516, var 25859357620.0027
  107 samples, mean -154068.0265, var 2233679635.6399
  77 samples, mean 325466.9154, var 2513237288.5835
  39 samples, mean 756376.7849, var 5388267076.9496
  49 samples, mean 517032.2460, var 3773697398.0887
  25 samples, mean -512944.0933, var 5600753222.7209
  36 samples, mean -951376.7330, var 114035847330.3548
  41 samples, mean -339962.6841, var 1966429555.8777
```

[**Raw results**](https://github.com/lianjiecao/envi/blob/master/results/raw.md) with more details.

<table>
  <tr>
    <th></th>
    <th colspan="6">HTTP_30KB</th>
  </tr>
  <tr>
    <td>Online options</td>
    <td>Accu</td>
    <td>0_Prec</td>
    <td>0_Reca</td>
    <td>1_Prec</td>
    <td>1_Reca</td>
    <td>AUROC</td>
  </tr>
  <tr>
    <td>scaler_none-clf_none</td>
    <td>0.42902</td>
    <td>0.42539</td>
    <td>1.0</td>
    <td>1.0</td>
    <td>0.01092</td>
    <td>0.98796</td>
  </tr>
  <tr>
    <td>scaler_none-clf_regular</td>
    <td>0.90220</td>
    <td>0.87050</td>
    <td>0.90298</td>
    <td>0.92696</td>
    <td>0.90163</td>
    <td>0.95359</td>
  </tr>
  <tr>
    <td>scaler_none-clf_window</td>
    <td>0.83280</td>
    <td>0.71657</td>
    <td>1.0</td>
    <td>1.0</td>
    <td>0.71038</td>
    <td>0.96562</td>
  </tr>
  <tr>
    <td>scaler_one-clf_none</td>
    <td>0.61514</td>
    <td>0.52343</td>
    <td>1.0</td>
    <td>1.0</td>
    <td>0.33333</td>
    <td>0.99449</td>
  </tr>
  <tr>
    <td>scaler_one-clf_regular</td>
    <td>0.90851</td>
    <td>0.87769</td>
    <td>0.91044</td>
    <td>0.93258</td>
    <td>0.90710</td>
    <td>0.97039</td>
  </tr>
  <tr>
    <td>scaler_one-clf_window</td>
    <td>0.90851</td>
    <td>0.88321</td>
    <td>0.90298</td>
    <td>0.92777</td>
    <td>0.91256</td>
    <td>0.95754</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_none</td>
    <td>0.76971</td>
    <td>0.82795</td>
    <td>0.57462</td>
    <td>0.74553</td>
    <td>0.91256</td>
    <td>0.80376</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_regular</td>
    <td>0.91167</td>
    <td>0.87857</td>
    <td>0.91791</td>
    <td>0.93785</td>
    <td>0.90710</td>
    <td>0.96497</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_window</td>
    <td>0.87381</td>
    <td>0.82191</td>
    <td>0.89552</td>
    <td>0.91812</td>
    <td>0.85792</td>
    <td>0.92684</td>
  </tr>
</table>


<table>
  <tr>
    <th></th>
    <th colspan="6">HTTP_50KB</th>
  </tr>
  <tr>
    <td>Online options</td>
    <td>Accu</td>
    <td>0_Prec</td>
    <td>0_Reca</td>
    <td>1_Prec</td>
    <td>1_Reca</td>
    <td>AUROC</td>
  </tr>
  <tr>
    <td>scaler_none-clf_none</td>
    <td>0.47949</td>
    <td>0.47949</td>
    <td>1.0</td>
    <td>0</td>
    <td>0.0</td>
    <td>0.99354</td>
  </tr>
  <tr>
    <td>scaler_none-clf_regular</td>
    <td>0.93375</td>
    <td>0.91719</td>
    <td>0.94736</td>
    <td>0.95</td>
    <td>0.92121</td>
    <td>0.97300</td>
  </tr>
  <tr>
    <td>scaler_none-clf_window</td>
    <td>0.90220</td>
    <td>0.90604</td>
    <td>0.88815</td>
    <td>0.89880</td>
    <td>0.91515</td>
    <td>0.97599</td>
  </tr>
  <tr>
    <td>scaler_one-clf_none</td>
    <td>0.57728</td>
    <td>0.53146</td>
    <td>1.0</td>
    <td>1.0</td>
    <td>0.18787</td>
    <td>0.99617</td>
  </tr>
  <tr>
    <td>scaler_one-clf_regular</td>
    <td>0.97160</td>
    <td>0.97350</td>
    <td>0.96710</td>
    <td>0.96987</td>
    <td>0.97575</td>
    <td>0.99669</td>
  </tr>
  <tr>
    <td>scaler_one-clf_window</td>
    <td>0.70977</td>
    <td>0.92857</td>
    <td>0.42763</td>
    <td>0.64777</td>
    <td>0.96969</td>
    <td>0.94314</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_none</td>
    <td>0.58044</td>
    <td>0.53429</td>
    <td>0.97368</td>
    <td>0.9</td>
    <td>0.21818</td>
    <td>0.87547</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_regular</td>
    <td>0.94321</td>
    <td>0.93506</td>
    <td>0.94736</td>
    <td>0.95092</td>
    <td>0.93939</td>
    <td>0.98401</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_window</td>
    <td>0.82334</td>
    <td>0.83802</td>
    <td>0.78289</td>
    <td>0.81142</td>
    <td>0.86060</td>
    <td>0.87775</td>
  </tr>
</table>



<table>
  <tr>
    <th></th>
    <th colspan="6">HTTP_70KB</th>
  </tr>
  <tr>
    <td>Online options</td>
    <td>Accu</td>
    <td>0_Prec</td>
    <td>0_Reca</td>
    <td>1_Prec</td>
    <td>1_Reca</td>
    <td>AUROC</td>
  </tr>
  <tr>
    <td>scaler_none-clf_none</td>
    <td>0.43962</td>
    <td>0.43962</td>
    <td>1.0</td>
    <td>0</td>
    <td>0.0</td>
    <td>0.96198</td>
  </tr>
  <tr>
    <td>scaler_none-clf_regular</td>
    <td>0.91950</td>
    <td>0.92028</td>
    <td>0.89436</td>
    <td>0.91891</td>
    <td>0.93922</td>
    <td>0.97136</td>
  </tr>
  <tr>
    <td>scaler_none-clf_window</td>
    <td>0.81733</td>
    <td>1.0</td>
    <td>0.58450</td>
    <td>0.75416</td>
    <td>1.0</td>
    <td>0.98323</td>
  </tr>
  <tr>
    <td>scaler_one-clf_none</td>
    <td>0.63467</td>
    <td>0.54651</td>
    <td>0.99295</td>
    <td>0.98461</td>
    <td>0.35359</td>
    <td>0.99167</td>
  </tr>
  <tr>
    <td>scaler_one-clf_regular</td>
    <td>0.95356</td>
    <td>0.95035</td>
    <td>0.94366</td>
    <td>0.95604</td>
    <td>0.96132</td>
    <td>0.99256</td>
  </tr>
  <tr>
    <td>scaler_one-clf_window</td>
    <td>0.64705</td>
    <td>1.0</td>
    <td>0.19718</td>
    <td>0.61355</td>
    <td>1.0</td>
    <td>0.99179</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_none</td>
    <td>0.47678</td>
    <td>0.45360</td>
    <td>0.92957</td>
    <td>0.6875</td>
    <td>0.12154</td>
    <td>0.80149</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_regular</td>
    <td>0.93808</td>
    <td>0.93571</td>
    <td>0.92253</td>
    <td>0.93989</td>
    <td>0.95027</td>
    <td>0.98435</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_window</td>
    <td>0.78018</td>
    <td>1.0</td>
    <td>0.5</td>
    <td>0.71825</td>
    <td>1.0</td>
    <td>0.97778</td>
  </tr>
</table>


<table>
  <tr>
    <th></th>
    <th colspan="6">HTTP_90KB</th>
  </tr>
  <tr>
    <td>Online options</td>
    <td>Accu</td>
    <td>0_Prec</td>
    <td>0_Reca</td>
    <td>1_Prec</td>
    <td>1_Reca</td>
    <td>AUROC</td>
  </tr>
  <tr>
    <td>scaler_none-clf_none</td>
    <td>0.48318</td>
    <td>0.48318</td>
    <td>1.0</td>
    <td>0</td>
    <td>0.0</td>
    <td>0.96329</td>
  </tr>
  <tr>
    <td>scaler_none-clf_regular</td>
    <td>0.92048</td>
    <td>0.91772</td>
    <td>0.91772</td>
    <td>0.92307</td>
    <td>0.92307</td>
    <td>0.97206</td>
  </tr>
  <tr>
    <td>scaler_none-clf_window</td>
    <td>0.74311</td>
    <td>0.98684</td>
    <td>0.47468</td>
    <td>0.66932</td>
    <td>0.99408</td>
    <td>0.97633</td>
  </tr>
  <tr>
    <td>scaler_one-clf_none</td>
    <td>0.79816</td>
    <td>0.70535</td>
    <td>1.0</td>
    <td>1.0</td>
    <td>0.60946</td>
    <td>0.99483</td>
  </tr>
  <tr>
    <td>scaler_one-clf_regular</td>
    <td>0.96941</td>
    <td>0.97435</td>
    <td>0.96202</td>
    <td>0.96491</td>
    <td>0.97633</td>
    <td>0.99760</td>
  </tr>
  <tr>
    <td>scaler_one-clf_window</td>
    <td>0.59327</td>
    <td>1.0</td>
    <td>0.15822</td>
    <td>0.55960</td>
    <td>1.0</td>
    <td>0.98831</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_none</td>
    <td>0.54740</td>
    <td>0.51689</td>
    <td>0.96835</td>
    <td>0.83870</td>
    <td>0.15384</td>
    <td>0.83974</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_regular</td>
    <td>0.95107</td>
    <td>0.95512</td>
    <td>0.94303</td>
    <td>0.94736</td>
    <td>0.95857</td>
    <td>0.97468</td>
  </tr>
  <tr>
    <td>scaler_multi-clf_window</td>
    <td>0.82874</td>
    <td>1.0</td>
    <td>0.64556</td>
    <td>0.75111</td>
    <td>1.0</td>
    <td>0.99202</td>
  </tr>
</table>

