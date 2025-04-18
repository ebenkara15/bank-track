import { Box, Flex, useColorModeValue } from "@chakra-ui/react";
import { Outlet, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import AccountVerifier from "./components/accounts/accountVerifier";
import Accounts from "./components/accounts/accounts";
import Categories from "./components/categories/categories";
import Home from "./components/home/Home";
import Sidebar from "./components/sidebar/Sidebar";
import Transactions from "./components/transactions/transactions";
import { BankDataProvider } from "./provider/BankDataProvider";


// const smVariant = { navigation: 'drawer', navigationButton: true }
// const mdVariant = { navigation: 'sidebar', navigationButton: false }

const Layout = () => {
  // const [isSidebarOpen, setSidebarOpen] = useState(false)
  // const variants = useBreakpointValue({ base: smVariant, md: mdVariant })

  // const toggleSidebar = () => setSidebarOpen(!isSidebarOpen)
  const bgColor = useColorModeValue("gray.50", "ui.dark")

  return (
    <BankDataProvider>
      <Flex h="auto" position="relative">
        <Sidebar />
        <Box bg={bgColor} p={5} w="100%">
          <Outlet />
        </Box>
      </Flex>
    </BankDataProvider >
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/accounts/verify" element={<AccountVerifier />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/categories" element={<Categories />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
