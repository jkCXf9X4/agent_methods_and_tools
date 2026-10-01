// Small package with two models, to demonstrate multi-model export:
//   python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
//     --load-file package.mo --model MyLib.Bounce --model MyLib.Springs \
//     --output-dir build/fmus
package MyLib
  model Bounce
    Real h(start = 1.0);
    Real v(start = 0.0);
  equation
    der(h) = v;
    der(v) = -9.81;
  end Bounce;

  model Springs
    parameter Real k = 2.0;
    Real x(start = 0.1);
  equation
    der(x) = -k * x;
  end Springs;
end MyLib;