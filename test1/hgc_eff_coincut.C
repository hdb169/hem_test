void HGC_EFF_COINCUT(){
  gStyle->SetOptStat(0);
  TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("coin_replay_production_3435_-1.root");
  if (!f) {
    f = new TFile("coin_replay_production_3435_-1.root"); //
  }
  // TH1F *hPass = new TH1F("hpass","",20,-10,20);
  TH2F *h = new TH2F("h","Efficiency vs Delta 3435 P = +3.37",20,-10,20,100,0,1);
  TH1F *hTotal[40];
  TH1F *hPass[40];
  
  //  Double_t aero[40];
  for (int k=0;k<40;k++)
    {
      //aero[k]=0.1+k/10.0;
      // cout<<aero[k]<<endl;
      hTotal[k] = new TH1F(Form("h_%d",k),"",20,-10,20);
      hPass[k] = new TH1F(Form("hp_%d",k),"",20,-10,20);
      
    }

  Double_t pgtrbeta,pgtrdp,paeronpesum,pcaleprtracknorm,pcaletottracknorm,pngcernpesum,phgcernpesum,pdcxfp,pdcxpfp,pcaletracknorm,pcaletotnorm,ctime,ctime_cut;
 
  TTree *tree = (TTree*) f->Get("T");
 
  tree->SetBranchAddress("CTime.ePiCoinTime_ROC2" ,&ctime);
  tree->SetBranchAddress("P.gtr.beta" ,&pgtrbeta);
  tree->SetBranchAddress("P.gtr.dp" ,&pgtrdp);
  tree->SetBranchAddress("P.cal.eprtracknorm" ,&pcaleprtracknorm);
  tree->SetBranchAddress("P.cal.etottracknorm" ,&pcaletottracknorm);
  tree->SetBranchAddress("P.ngcer.npeSum" ,&pngcernpesum);
  tree->SetBranchAddress("P.hgcer.npeSum" ,&phgcernpesum);
  tree->SetBranchAddress("P.aero.npeSum" ,&paeronpesum);
  tree->SetBranchAddress("P.dc.x_fp" ,&pdcxfp);
  tree->SetBranchAddress("P.dc.xp_fp" ,&pdcxpfp);
  tree->SetBranchAddress("P.cal.etracknorm" ,&pcaletracknorm);
  tree->SetBranchAddress("P.cal.etotnorm" ,&pcaletotnorm);

  const int n = 40;
  TH1D *ct_ = new TH1D ("ct_","SHMS ROC2 Corrected epi Coin Time; cointime [ns]",500,-50,50);
  //TH1D *ct2[10];
  //TH1D *ct2 = (TH1D*)ct->Clone("ct2");
  //TH1D *ct3 = (TH1D*)ct->Clone("ct3");
  TH1D *ct[n];

  char tempc[500];
  
  for(int i=0; i<n ; i++){
    sprintf(tempc,"ct_%d",i);
    //ct[i] = new TH1D (tempc,"SHMS ROC2 Corrected epi Coin Time; cointime [ns]",500,-50,50);
    ct[i] = new TH1D (tempc,tempc,500,-50.,50.);
  }
  
  Long64_t nentries =tree->GetEntries();

  
  Double_t cutmin[n];
  Double_t cutmax[n];
  double step = 0.1; // (ns)
  
  for(int i=0; i<n ; i++){
    cutmin[i] = 0.0;
    cutmax[i] = 0.0;
  }
    
  for(int i=0; i<n ; i++){
    cutmin[i] = cutmin[i]-step*i -0.5;
    cutmax[i] = cutmax[i]+step*i +0.5;
    cout << cutmin[i] << " " << cutmax[i] << endl;
  }

  double ctime_cor;
  for (Long64_t i=0; i<nentries; i++) 
    {
      ctime_cor = -2222.0;
      
      tree->GetEntry(i);
      ctime_cor = ctime - 9.82;
      for(int j=0; j<n ; j++){
	if(cutmin[j]<ctime_cor && ctime_cor<cutmax[j]  &&  pgtrbeta>0.8&&pgtrbeta<1.10&&pgtrdp<20&&pgtrdp>-10&&paeronpesum>3.0 )


	  {
	    // hTotal[j]->Fill(ctime_cor);
	    hTotal[j]->Fill(pgtrdp);
	  }
	if(cutmin[j]<ctime_cor && ctime_cor<cutmax[j]  &&  pgtrbeta>0.8&&pgtrbeta<1.3&&pgtrdp<20&&pgtrdp>-10&&paeronpesum>3.0 &&phgcernpesum>0.5 )
	  {
	    // hPass[j]->Fill(ctime_cor);
	    hPass[j]->Fill(pgtrdp);
	  }
      }
      //	cout<<hTotal[i]->GetEntries()<<endl;  
      
    }
  Double_t Should[40];
  Double_t eff[40];
  Double_t Did[40];
  //TGraph *gr = new TGraph();
  TMultiGraph *mg = new TMultiGraph();
  
  for (int i=0; i<20; i++)
    {
      Should[i] = hTotal[i]->GetEntries();
      Did[i]=hPass[i]->GetEntries();
      
      // cout<<"Should Pass Events =<<"Should[i]<< "\t" <<"Did Pass Events = "<<Did[i]<< endl;
      
      if(Did[i] == 0)
	cout << "SHMS hgcer efficiency: "<< 0 <<" %"<<endl;
      else
	//	cout << "SHMS hgcer efficiency: "<< Did*100/Should[i] <<" %"<<endl;
	{
	  eff[i]=Did[i]*100/Should[i];
	}
      cout<<"Should Pass Events ="<<Should[i]<< "\t" <<"Did Pass Events = "<<Did[i]<< "\t" << "Efficiency = "<<eff[i]<<endl;//cout<<setprecision(6) : 6 digit numbers

      // gr->SetPoint(i, cutmax, eff);
    }
  Int_t n1 = 40;
  TCanvas *c11 = new TCanvas("c11", "", 500,500);
  TGraph *gr =new TGraph(n1, cutmax, eff);
  TGraph *gr1 =new TGraph(n1, cutmin, eff);
  gr1->SetMarkerColor(2);
  mg->Add(gr);
  mg->Add(gr1);
  mg->Draw("AP*");
  
  //gr->Draw("AP*");
}

