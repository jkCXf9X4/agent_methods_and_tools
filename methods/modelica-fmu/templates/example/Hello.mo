// Minimal balanceable Modelica model: first-order decay.
// Export with:
//   python3 3rd_party/article_common_artifacts/modelica/build_fmu.py \
//     --load-file Hello.mo --model HelloWorld --output-dir build/fmus
model HelloWorld
  Real x(start = 1.0);
equation
  der(x) = -x;
end HelloWorld;