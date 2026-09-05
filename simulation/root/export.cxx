// Compiled ROOT columnar export; avoids Cling/JIT and graphics.
// https://root.cern/manual/trees/
#include <TFile.h>
#include <TROOT.h>
#include <TTree.h>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <regex>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

std::vector<std::string> split(std::string line) {
  if (!line.empty() && line.back() == '\r') line.pop_back();
  std::vector<std::string> fields;
  std::stringstream input(line);
  std::string field;
  while (std::getline(input, field, ',')) fields.push_back(field);
  return fields;
}

int main(int argc, char **argv) {
  if (argc != 4) throw std::runtime_error("Expected trajectory.csv output.root summary.json");
  gROOT->SetBatch(true);
  std::ifstream input(argv[1]);
  if (!input) throw std::runtime_error("Cannot open input CSV");
  std::string line;
  std::getline(input, line);
  const auto names = split(line);
  if (std::set<std::string>(names.begin(), names.end()).size() != names.size())
    throw std::runtime_error("Duplicate CSV columns");
  const auto column = [&](const std::string &name) {
    auto found = std::find(names.begin(), names.end(), name);
    if (found == names.end()) throw std::runtime_error("Missing column: " + name);
    return static_cast<size_t>(found - names.begin());
  };
  const auto time_column = column("time_s");
  const auto speed_column = column("wheel_x_relative_rad_s");
  for (const auto &name : names)
    if (name == "sample_dt_s" || !std::regex_match(name, std::regex("[A-Za-z_][A-Za-z0-9_]*")))
      throw std::runtime_error("Only generated numeric trajectory columns are supported");
  std::vector<std::vector<double>> rows;
  while (std::getline(input, line)) {
    const auto fields = split(line);
    if (fields.size() != names.size()) throw std::runtime_error("Wrong CSV row width");
    std::vector<double> row;
    for (const auto &field : fields) {
      size_t end = 0;
      double value = std::stod(field, &end);
      if (end != field.size() || !std::isfinite(value)) throw std::runtime_error("Non-finite/non-numeric CSV value");
      row.push_back(value);
    }
    if (!rows.empty() && row[time_column] <= rows.back()[time_column])
      throw std::runtime_error("Timestamps must increase strictly");
    rows.push_back(std::move(row));
  }
  if (rows.size() < 2) throw std::runtime_error("At least two recorded rows are required");
  std::vector<double> weights(rows.size(), 0);
  double seconds = 0, weighted_speed = 0, maximum_rpm = 1;
  for (size_t i = 0; i < rows.size(); ++i) {
    if (i + 1 < rows.size()) weights[i] = rows[i + 1][time_column] - rows[i][time_column];
    const double rpm = rows[i][speed_column] * 60 / (2 * std::acos(-1.0));
    seconds += weights[i];
    weighted_speed += rpm * weights[i];
    maximum_rpm = std::max(maximum_rpm, std::abs(rpm));
  }
  std::vector<double> histogram(80, 0);
  const double extent = maximum_rpm * 1.05 + 1;
  const double width = 2 * extent / histogram.size();
  for (size_t i = 0; i < rows.size(); ++i) {
    const double rpm = rows[i][speed_column] * 60 / (2 * std::acos(-1.0));
    const auto bin = static_cast<size_t>((rpm + extent) / width);
    if (bin >= histogram.size()) throw std::runtime_error("Histogram range error");
    histogram[bin] += weights[i];
  }
  {
    TFile file(argv[2], "CREATE");
    if (file.IsZombie()) throw std::runtime_error("Cannot create new ROOT file");
    std::vector<double> values(names.size() + 1);
    TTree tree("trajectory", "WIP MuJoCo records; not physical qualification");
    for (size_t i = 0; i < names.size(); ++i)
      tree.Branch(names[i].c_str(), &values[i], (names[i] + "/D").c_str());
    tree.Branch("sample_dt_s", &values.back(), "sample_dt_s/D");
    for (size_t i = 0; i < rows.size(); ++i) {
      std::copy(rows[i].begin(), rows[i].end(), values.begin());
      values.back() = weights[i];
      tree.Fill();
    }
    tree.Write();
    tree.ResetBranchAddresses();
    double lower, upper, duration;
    TTree bins("time_weighted_wheel_x_rpm", "Left-hold descriptive histogram; not work integration");
    bins.Branch("lower_rpm", &lower, "lower_rpm/D");
    bins.Branch("upper_rpm", &upper, "upper_rpm/D");
    bins.Branch("simulated_seconds", &duration, "simulated_seconds/D");
    for (size_t i = 0; i < histogram.size(); ++i) {
      lower = -extent + i * width;
      upper = lower + width;
      duration = histogram[i];
      bins.Fill();
    }
    bins.Write();
    bins.ResetBranchAddresses();
  }
  {
    TFile file(argv[2], "READ");
    auto *tree = file.Get<TTree>("trajectory");
    if (!tree || tree->GetEntries() != static_cast<Long64_t>(rows.size()))
      throw std::runtime_error("ROOT row-count mismatch");
    std::vector<double> values(names.size() + 1);
    for (size_t i = 0; i < names.size(); ++i)
      if (tree->SetBranchAddress(names[i].c_str(), &values[i]) < 0)
        throw std::runtime_error("ROOT branch binding failed");
    if (tree->SetBranchAddress("sample_dt_s", &values.back()) < 0)
      throw std::runtime_error("ROOT time-weight binding failed");
    for (size_t i = 0; i < rows.size(); ++i) {
      if (tree->GetEntry(i) <= 0) throw std::runtime_error("ROOT entry read failed");
      for (size_t j = 0; j < names.size(); ++j)
        if (values[j] != rows[i][j]) throw std::runtime_error("ROOT round-trip value mismatch");
      if (values.back() != weights[i]) throw std::runtime_error("ROOT time-weight mismatch");
    }
    tree->ResetBranchAddresses();
  }
  std::ofstream summary(argv[3]);
  summary << std::setprecision(17)
          << "{\"status\":\"NATIVE_TTREE_ROUNDTRIP_VALIDATED\",\"root_version\":\""
          << gROOT->GetVersion() << "\",\"rows\":" << rows.size()
          << ",\"source_columns\":" << names.size()
          << ",\"weighted_seconds\":" << seconds
          << ",\"time_weighted_mean_x_rpm\":" << weighted_speed / seconds
          << ",\"graphics_or_RDataFrame_exercised\":false}\n";
  if (!summary) throw std::runtime_error("Cannot write ROOT summary");
  std::cout << "NATIVE_TTREE_ROUNDTRIP_VALIDATED " << rows.size() << '\n';
}
