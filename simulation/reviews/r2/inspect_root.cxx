// Independent scalar-tree reader. No Cling expressions, graphics or export code.
#include <TFile.h>
#include <TLeaf.h>
#include <TObjArray.h>
#include <TTree.h>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
  try {
    if (argc != 2) throw std::runtime_error("Expected one existing ROOT file");
    TFile file(argv[1], "READ");
    if (file.IsZombie()) throw std::runtime_error("ROOT read failed");
    std::cout << std::setprecision(17) << "{";
    bool first = true;
    for (const char* name : {"trajectory", "time_weighted_wheel_x_rpm"}) {
      auto* tree = file.Get<TTree>(name);
      if (!tree) throw std::runtime_error("Missing tree");
      if (!first) std::cout << ",";
      first = false;
      auto* leaves = tree->GetListOfLeaves();
      std::cout << std::quoted(name) << ":{\"columns\":[";
      for (int j = 0; j < leaves->GetEntries(); ++j) {
        auto* leaf = dynamic_cast<TLeaf*>(leaves->At(j));
        if (!leaf || std::string(leaf->GetTypeName()) != "Double_t" || leaf->GetLenStatic() != 1)
          throw std::runtime_error("Expected scalar double leaf");
        if (j) std::cout << ",";
        std::cout << std::quoted(leaf->GetName());
      }
      std::cout << "],\"values\":[";
      for (Long64_t i = 0; i < tree->GetEntries(); ++i) {
        if (tree->GetEntry(i) <= 0) throw std::runtime_error("Entry read failed");
        if (i) std::cout << ",";
        std::cout << "[";
        for (int j = 0; j < leaves->GetEntries(); ++j) {
          double value = static_cast<TLeaf*>(leaves->At(j))->GetValue();
          if (!std::isfinite(value)) throw std::runtime_error("Nonfinite ROOT value");
          if (j) std::cout << ",";
          std::cout << value;
        }
        std::cout << "]";
      }
      std::cout << "]}";
    }
    std::cout << "}\n";
    return 0;
  } catch (const std::exception& e) {
    std::cerr << e.what() << "\n";
    return 1;
  }
}
