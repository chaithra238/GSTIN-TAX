import React, { useState } from "react";
import axios from "axios";
import "./getSearch.css";

export default function GetSearch() {

    const [query, setQuery] = useState("");

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");

    const [result, setResult] = useState<any>(null);

    const handleSearch = async (e: React.FormEvent) => {

        e.preventDefault();

        setError("");
        setResult(null);

        const gstRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{3}$/;

        if (!gstRegex.test(query)) {

            setError("Please enter a valid GSTIN.");

            return;

        }

        setLoading(true);

        try {

            const response = await axios.get(
                "http://127.0.0.1:8000/api/search/",
                {
                    params: {
                        query: query
                    }
                }
            );

            console.log(response.data);

            setResult(response.data);

        }

        catch (err) {

            console.log(err);

            setError("Unable to fetch GST Details.");

        }

        finally {

            setLoading(false);

        }

    };

    return (

        <div className="container">

            <div className="card">

                <h1>GST Search Engine</h1>

                <p className="subtitle">

                    Search GST Details from Multiple Verification Portals

                </p>

                <form onSubmit={handleSearch}>

                    <input

                        type="text"

                        placeholder="Enter GSTIN"

                        value={query}

                        onChange={(e) =>
                            setQuery(e.target.value.toUpperCase())
                        }

                    />

                    <button type="submit">

                        Search

                    </button>

                </form>

            </div>

            {loading && (

                <div className="loading">

                    <div className="spinner"></div>

                    <p>Searching GST Details...</p>

                </div>

            )}

            {error && (

                <div className="errorCard">

                    ❌ {error}

                </div>

            )}

            {result && result.status === "success" && (

<div className="dashboard">

    <div className="section">

        <h2>🏢 Business Information</h2>

        <div className="grid">

            <div>
                <span>GSTIN</span>
                <p>{result.data.gstin}</p>
            </div>

            <div>
                <span>Business Name</span>
                <p>{result.data.business_name || "-"}</p>
            </div>

            <div>
                <span>Legal Name</span>
                <p>{result.data.legal_name || "-"}</p>
            </div>

            <div>
                <span>Status</span>

                <p className={
                    result.data.gst_status === "Active"
                    ? "active"
                    : "inactive"
                }>

                    {result.data.gst_status}

                </p>

            </div>

        </div>

    </div>

    <div className="section">

        <h2>📅 Registration Details</h2>

        <div className="grid">

            <div>

                <span>Registration Date</span>

                <p>{result.data.registration_date || "-"}</p>

            </div>

            <div>

                <span>Last Updated</span>

                <p>{result.data.last_updated || "-"}</p>

            </div>

            <div>

                <span>Constitution</span>

                <p>{result.data.constitution || "-"}</p>

            </div>

            <div>

                <span>Taxpayer Type</span>

                <p>{result.data.taxpayer_type || "-"}</p>

            </div>

        </div>

    </div>

    <div className="section">

        <h2>📍 Business Address</h2>

        <div className="grid">

            <div className="fullWidth">

                <span>Principal Address</span>

                <p>{result.data.principal_place || "-"}</p>

            </div>

            <div>

                <span>State</span>

                <p>{result.data.state || "-"}</p>

            </div>

            <div>

                <span>District</span>

                <p>{result.data.district || "-"}</p>

            </div>

            <div>

                <span>Center Jurisdiction</span>

                <p>{result.data.center_jurisdiction || "-"}</p>

            </div>

            <div>

                <span>State Jurisdiction</span>

                <p>{result.data.state_jurisdiction || "-"}</p>

            </div>

            <div>

                <span>Nature Of Business</span>

                <p>{result.data.nature_of_business || "-"}</p>

            </div>

        </div>

    </div>

    
</div>

)}
            

        </div>

    );

}