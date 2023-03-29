module \$_ADDER_ (a, b,cin,s,cout);
    input a, b,cin;
    output s,cout;

    adder _TECHMAP_REPLACE_ (.a(a), .b(b), .cin(cin), .s(s), .cout(cout));

endmodule
