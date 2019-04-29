function inp = transferfunc_winter(y0)
    %setpoint = cell2mat(transpose(setpoint));
    %assignin('base','setpoint',double(setpoint));
    assignin('base','y0',y0);
    Tau = 3600;                                                             %Settling Time 120 min
    kp = 4;                                                                 %Delta T/Delta U
    delay = 120;                                                            %15 min delay 
    Ts = 1800;                                                              %Sampling Time 30 min
    p = 48;                                                                 %Prediction Horizon 
    m = 20; 
    y0 = 22;
    plant = tf(kp,[Tau 1],'InputDelay',delay); 
    open_system('mpc_winter1')
    mpcobj = mpc(plant, Ts, p, m);
    mpcobj.MV.Max = 1;
    mpcobj.MV.Min = 0;
    display(mpcobj)
    set_param('mpc_winter1/Subsystem/Constant','Value',int2str(y0));
    simout = sim('mpc_winter1','SaveOutput','on','OutputSaveName','u');
    inp = simout.get('u');
end