import { Layout } from "antd";
import "antd/dist/reset.css";
import "./App.css";

import DoubanDashboard from "./components/DoubanDashboard";

const { Header, Content } = Layout;

function App() {
  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="app-logo">Douban Movie Analysis</div>
      </Header>

      <Content className="app-content">
        <DoubanDashboard />
      </Content>
    </Layout>
  );
}

export default App;